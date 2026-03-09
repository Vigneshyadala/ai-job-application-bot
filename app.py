from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import glob
import json
import subprocess
import threading
from datetime import datetime
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'data'

# Global variables
bot_process = None
bot_running = False
config_file = 'bot_config.json'

ALLOWED_EXTENSIONS = {'pdf'}

# Company categories
COMPANY_CATEGORIES = {
    'indian_it': {
        'name': 'Indian IT Giants',
        'companies': ['TCS', 'Infosys', 'Wipro', 'HCLTech', 'Tech Mahindra', 'Accenture', 'Cognizant']
    },
    'faang': {
        'name': 'FAANG + Big Tech',
        'companies': ['Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Oracle', 'IBM']
    }
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_resume_text(pdf_path):
    """Extract text from resume PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"Error reading resume: {str(e)}"

def get_resume_info():
    """Get current resume information"""
    resume_path = os.path.join('data', 'resume.pdf')
    if os.path.exists(resume_path):
        stat_info = os.stat(resume_path)
        return {
            'exists': True,
            'filename': 'resume.pdf',
            'size': f"{stat_info.st_size / 1024:.1f} KB",
            'uploaded': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    return {'exists': False}

@app.route('/')
def index():
    resume_info = get_resume_info()
    return render_template('index.html', resume_info=resume_info)

@app.route('/api/stats')
def get_stats():
    """Get statistics from CSV files"""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        stats = {
            'total_applications': 0,
            'successful_applications': 0,
            'pending_applications': 0,
            'average_match_score': 0,
            'companies': {},
            'recent_jobs': []
        }
        
        csv_files = glob.glob(os.path.join(data_dir, 'job_results_*.csv'))
        
        if not csv_files:
            return jsonify(stats)
        
        all_jobs = []
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if not df.empty:
                    all_jobs.append(df)
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
                continue
        
        if not all_jobs:
            return jsonify(stats)
        
        combined_df = pd.concat(all_jobs, ignore_index=True)
        
        stats['total_applications'] = len(combined_df)
        
        # Count applications marked as applied
        if 'applied' in combined_df.columns:
            stats['successful_applications'] = int(combined_df['applied'].sum())
            stats['pending_applications'] = int((~combined_df['applied']).sum())
        elif 'should_apply' in combined_df.columns:
            stats['successful_applications'] = int(combined_df['should_apply'].sum())
        
        # Match score
        if 'match_score' in combined_df.columns:
            try:
                scores = pd.to_numeric(combined_df['match_score'], errors='coerce')
                stats['average_match_score'] = float(scores.mean())
            except:
                stats['average_match_score'] = 0
        
        # Companies
        if 'company' in combined_df.columns:
            company_counts = combined_df['company'].value_counts()
            stats['companies'] = {str(k): int(v) for k, v in company_counts.items()}
        
        # Recent jobs (last 20)
        recent_df = combined_df.tail(20)
        
        for _, row in recent_df.iterrows():
            job = {
                'company': str(row.get('company', 'N/A')),
                'title': str(row.get('title', 'N/A')),
                'location': str(row.get('location', 'N/A')),
                'match_score': str(int(row.get('match_score', 0))),
                'status': 'Applied' if row.get('applied', False) else 'Pending',
                'date': str(row.get('timestamp', datetime.now().strftime('%Y-%m-%d')))[:10]
            }
            stats['recent_jobs'].append(job)
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error in get_stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'total_applications': 0,
            'successful_applications': 0,
            'pending_applications': 0,
            'average_match_score': 0,
            'companies': {},
            'recent_jobs': []
        })

@app.route('/api/company-categories')
def get_company_categories():
    """Get available company categories"""
    return jsonify(COMPANY_CATEGORIES)

@app.route('/api/resume', methods=['GET'])
def get_resume():
    """Get resume information"""
    return jsonify(get_resume_info())

@app.route('/api/resume/upload', methods=['POST'])
def upload_resume():
    """Upload resume PDF"""
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Only PDF files are allowed'}), 400
        
        # Save the file
        filename = secure_filename('resume.pdf')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract and validate
        text = extract_resume_text(filepath)
        if len(text.strip()) < 100:
            os.remove(filepath)
            return jsonify({'success': False, 'message': 'Resume seems too short or unreadable'}), 400
        
        resume_info = get_resume_info()
        return jsonify({
            'success': True, 
            'message': 'Resume uploaded successfully!',
            'resume_info': resume_info,
            'preview': text[:500] + '...' if len(text) > 500 else text
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/start-bot', methods=['POST'])
def start_bot():
    """Start the bot with selected companies"""
    global bot_process, bot_running
    
    try:
        config = request.json
        
        # Check if resume exists
        resume_path = os.path.join('data', 'resume.pdf')
        if not os.path.exists(resume_path):
            return jsonify({
                'status': 'error', 
                'message': 'Please upload your resume first!'
            })
        
        # Validate configuration
        if not config.get('companies') or len(config['companies']) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Please select at least one company or Naukri'
            })
        
        # Save configuration to temporary file
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"Starting bot with config: {config}")
        
        # Check if bot is already running
        if bot_running:
            return jsonify({'status': 'error', 'message': 'Bot is already running'})
        
        # Create input file for the bot to simulate user selection
        input_data = {
            'companies': config.get('companies', []),
            'roles': config.get('roles', ['Python Developer', 'Software Engineer']),
            'locations': config.get('locations', ['Bangalore', 'Mumbai']),
            'min_experience': config.get('minExperience', 0),
            'max_experience': config.get('maxExperience', 5)
        }
        
        with open('bot_input.json', 'w') as f:
            json.dump(input_data, f, indent=4)
        
        # Start bot in background thread
        def run_bot():
            global bot_process, bot_running
            bot_running = True
            try:
                # Run the enhanced_main.py
                # Note: You'll need to modify enhanced_main.py to accept config file
                bot_process = subprocess.Popen(
                    ['python', 'enhanced_main.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )
                
                # Send company selection to stdin
                companies_str = ','.join([str(i+1) for i, c in enumerate(config['companies'])])
                bot_process.stdin.write(f"{companies_str}\n".encode())
                bot_process.stdin.flush()
                
                bot_process.wait()
            except Exception as e:
                print(f"Error running bot: {e}")
            finally:
                bot_running = False
                bot_process = None
        
        thread = threading.Thread(target=run_bot)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': f'Bot started! Searching on {len(config.get("companies", []))} platforms',
            'config': config
        })
        
    except Exception as e:
        print(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop-bot', methods=['POST'])
def stop_bot():
    """Stop the running bot"""
    global bot_process, bot_running
    
    try:
        if bot_process and bot_running:
            bot_process.terminate()
            bot_running = False
            return jsonify({'status': 'success', 'message': 'Bot stopped'})
        else:
            return jsonify({'status': 'error', 'message': 'No bot is running'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/bot-status')
def bot_status():
    """Check if bot is running"""
    global bot_running
    return jsonify({'running': bot_running})

@app.route('/api/save-settings', methods=['POST'])
def save_settings():
    """Save bot settings to .env file"""
    try:
        settings = request.json
        
        env_file = '.env'
        env_content = []
        
        # Read existing .env
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_content = f.readlines()
        
        # Settings mapping
        settings_map = {
            'apiKey': 'GOOGLE_API_KEY',
            'minMatchScore': 'MIN_MATCH_SCORE',
            'maxApps': 'MAX_APPLICATIONS_PER_DAY',
            'autoApply': 'AUTO_APPLY',
            'desiredRoles': 'DESIRED_ROLES',
            'desiredLocations': 'DESIRED_LOCATIONS',
            'minExperience': 'MIN_EXPERIENCE',
            'maxExperience': 'MAX_EXPERIENCE',
            'naukriEmail': 'NAUKRI_EMAIL',
            'naukriPassword': 'NAUKRI_PASSWORD'
        }
        
        # Update or add settings
        for key, env_key in settings_map.items():
            if key in settings:
                value = settings[key]
                found = False
                
                for i, line in enumerate(env_content):
                    if line.startswith(f'{env_key}='):
                        env_content[i] = f'{env_key}={value}\n'
                        found = True
                        break
                
                if not found:
                    env_content.append(f'{env_key}={value}\n')
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(env_content)
        
        return jsonify({'status': 'success', 'message': 'Settings saved successfully!'})
        
    except Exception as e:
        print(f"Error saving settings: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/load-settings')
def load_settings():
    """Load current settings from .env"""
    try:
        settings = {}
        env_file = '.env'
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Hide sensitive values
                        if 'PASSWORD' in key or 'API_KEY' in key:
                            settings[key] = '***HIDDEN***'
                        else:
                            settings[key] = value
        
        return jsonify({'status': 'success', 'settings': settings})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    try:
        log_dir = 'logs'
        log_files = glob.glob(os.path.join(log_dir, 'bot_*.log'))
        
        if not log_files:
            return jsonify({'logs': [], 'message': 'No logs available yet'})
        
        # Get most recent log file
        latest_log = max(log_files, key=os.path.getctime)
        
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            logs = f.readlines()[-100:]  # Last 100 lines
        
        return jsonify({'logs': logs, 'file': os.path.basename(latest_log)})
        
    except Exception as e:
        print(f"Error getting logs: {e}")
        return jsonify({'logs': [], 'error': str(e)})

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update bot configuration"""
    env_file = '.env'
    
    if request.method == 'POST':
        try:
            data = request.json
            
            # Read existing .env
            config_data = {}
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config_data[key.strip()] = value.strip()
            
            # Update with new values
            for key, value in data.items():
                config_data[key] = value
            
            # Write back
            with open(env_file, 'w') as f:
                f.write("# AI Job Application Bot Configuration\n")
                f.write(f"# Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for key, value in config_data.items():
                    f.write(f"{key}={value}\n")
            
            return jsonify({'success': True, 'message': 'Configuration saved!'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    else:  # GET
        config_data = {}
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Hide sensitive values
                        if 'PASSWORD' in key or 'API_KEY' in key:
                            value = '***HIDDEN***'
                        config_data[key.strip()] = value.strip()
        
        return jsonify(config_data)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 60)
    print("🚀 AI Job Application Bot - Enhanced Control Panel")
    print("=" * 60)
    print("🚀 AI Job Application Bot - Enhanced Control Panel")
    print("=" * 80)
    print("╔" + "═" * 78 + "╗")
    print("║           🤖 ENHANCED AI JOB APPLICATION BOT - MULTI COMPANY                 ║")
    print("║           👨‍💻 Developed by: Vignesh Yadala                                    ║")
    print("║           📅 Version: December 2025                                          ║")
    print("║           🚀 Powered by Google Gemini AI                                     ║")
    print("╚" + "═" * 78 + "╝")
    print("=" * 60)
    print(f"📂 Data directory: {os.path.abspath('data')}")
    print(f"🌐 Dashboard URL: http://localhost:5000")
    print(f"🤖 Bot status: Ready to start")
    print("=" * 60)
    print("✨ Features:")
    print("  📄 Resume upload via web interface")
    print("  🏢 Interactive company selection")
    print("  ⚙️ Settings editor in browser")
    print("  📊 Live statistics dashboard")
    print("  📝 Real-time log viewer")
    print("=" * 60)
    
    app.run(debug=True, port=5000, use_reloader=False)