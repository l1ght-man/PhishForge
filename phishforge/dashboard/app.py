from flask import Flask , render_template , request , redirect , url_for , flash
import os
import csv
from datetime import datetime
from flask import render_template , Response
from phishforge.models.database import *
from io import StringIO
from weasyprint import HTML, CSS

template_folder = '/app/templates'
app = Flask(__name__ , template_folder=template_folder)
app.secret_key = 'phishforge-dev-key-change-in-prod'
init_db()
PDF_OPTIONS = {
    'page-size' : 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None,
    'enable-local-file-access': None
}


@app.route('/')
def index():
    """Home: Campaign management only (no analytics)"""
    campaigns = get_campaigns()  # Reuse your existing function
    
    # Add victim/hit counts to each campaign
    conn = get_db_connection()
    for c in campaigns:
        c['victim_count'] = conn.execute(
            'SELECT COUNT(*) FROM victims WHERE campaign_id = ?', (c['id'],)
        ).fetchone()[0]
        c['hits_count'] = conn.execute(
            'SELECT COUNT(*) FROM hits WHERE campaign_id = ?', (c['id'],)
        ).fetchone()[0]
    conn.close()
    
    return render_template('index.html', campaigns=campaigns)
@app.route('/dashboard')
def dashboard():
      conn = get_db_connection()
    
    # Get campaign metrics
      campaigns = conn.execute('''
        SELECT c.id, c.name, c.email_subject,
               (SELECT COUNT(*) FROM victims WHERE campaign_id = c.id) as victim_count,
               (SELECT COUNT(*) FROM hits WHERE campaign_id = c.id) as hit_count
        FROM campaigns c
        ORDER BY c.id DESC
    ''').fetchall()
    
    # Process campaigns with conversion rates
      campaign_list = []
      for camp in campaigns:
        victim_count = camp['victim_count']
        hit_count = camp['hit_count']
        conversion_rate = round((hit_count / victim_count) * 100, 1) if victim_count > 0 else 0
        campaign_list.append({
            'id': camp['id'],
            'name': camp['name'],
            'subject': camp['email_subject'],
            'victim_count': victim_count,
            'hit_count': hit_count,
            'conversion_rate': conversion_rate
        })
    
    # Get recent hits
      recent_hits = conn.execute('''
        SELECT h.email, h.timestamp, c.name as campaign_name, h.campaign_id
        FROM hits h
        JOIN campaigns c ON h.campaign_id = c.id
        ORDER BY h.timestamp DESC
        LIMIT 5
    ''').fetchall()
    
    # Overall stats
      total_campaigns = len(campaigns)
      total_victims = sum(c['victim_count'] for c in campaign_list)
      total_hits = sum(c['hit_count'] for c in campaign_list)
      overall_conversion = round((total_hits / total_victims) * 100, 1) if total_victims > 0 else 0
      
      conn.close()
      
      return render_template('dashboard.html',
                              campaigns=campaign_list,
                              recent_hits=recent_hits,
                              total_campaigns=total_campaigns,
                              total_victims=total_victims,
                              total_hits=total_hits,
                              overall_conversion=overall_conversion)

@app.route('/demo' , methods = ['GET' , 'POST'])
def demo():
    if request.method == 'POST':
 
           username = request.form['username']
           password = request.form['password']
           timestap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           issues = analyse_phishing(username, password)
           risk = 'HIGH RISK' if issues else 'LOW RISK'
           log_entry = f" {timestap} | User: {username} | password: {password} | {risk} \n"
           with open("logs/phishing_logs.txt" , 'a') as f:
                  f.write(log_entry)
                  
           return render_template('results.html', issues=issues , risk= risk , log_entry=log_entry)
    return render_template('demo.html')

def analyse_phishing(username , password):
        issues =[]
        if len(password) < 6 and password in ['admin' , '12345' , 'admin']:
            issues.append("❌ Weak password (common phishing bait")
        if len(username) <5 and username.lower() in ['admin', 'administrator', 'root']:
            issues.append("❌ Suspicious username")
        if any(char.isdigit() for char in password) and len(password) < 3:
            issues.append("❌ Sequential/repeated chars")
        return issues


@app.route('/create', methods=['GET','POST'])
def create_campaign_view() :
      """creates a new phishing campaign"""
      if request.method == 'POST':
        name = request.form.get('name', '').strip()
        subject = request.form.get('subject', '').strip()
        email_html = request.form.get('email_html', '').strip()
        landing_html = request.form.get('landing_html', '').strip()
        if name and subject and email_html and landing_html :
              campaign_id = create_campaign(name, subject, email_html, landing_html)
              flash(f'Campaign "{name}" created! ID: {campaign_id}', 'success')
              return redirect('/')
        else :
              flash(f'please fill all the fields ')
      return render_template('create_campaign.html')
@app.route('/campaign/<int:compaign_id>') 
def compaign_details (compaign_id) :
      """view single compaign details """
      compaign = get_campaign(compaign_id)
      if not compaign:
            flash('compaign not found')
            return redirect(url_for('home'))
      return render_template('campaign_detail.html',compaign=compaign)

@app.route('/campaign/<int:campaign_id>/preview')
def campaign_preview(campaign_id):
    campaign = get_campaign(campaign_id)
    landing_url = f"http://localhost:3000/c/{campaign_id}"
    email_html = campaign['email_body_html'].replace('{{landing_url}}', landing_url)
    return render_template('preview.html', html=email_html)

@app.route('/campaign/<int:campaign_id>/upload_victims', methods= ['POST'])
def upload_victims (campaign_id):
     """upload CSV with victims (email, name , departement)"""
     if 'file' not in request.files:
          return "no file uploaded" , 400
     file = request.files['file']
     if file.filename == '' :
          return "No file selected" , 400
     csv_content = file.read().decode('utf-8')
     csv_reader = csv.DictReader(StringIO(csv_content))
     
     added = 0
     skipped = 0
     
     for row in csv_reader :
            email = row.get('email', '').strip()
            if not email:
                 continue
            results=add_victim(
            campaign_id=campaign_id,
            email=row['email'],
            name=row.get('name'),
            department=row.get('department')
          )
            if results:
                 added += 1
            else:
                 skipped +=1

     flash(f'Uploaded: {added} new , {skipped}duplicates skipped ', 'success')
     return redirect(f' /campaign/{campaign_id}/stats')

@app.route('/campaign/<int:campaign_id>/stats')
def campaign_stats(campaign_id):
    campaign = get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404
    
    conn = get_db_connection()
    
    # Get hits and victims
    hits = conn.execute('''
        SELECT email, password, ip_address, user_agent, timestamp
        FROM hits 
        WHERE campaign_id = ?
        ORDER BY timestamp DESC
    ''', (campaign_id,)).fetchall()
    
    victims = get_victims(campaign_id)
    victims.sort(key=lambda v:(
         v.get('department','').lower() if v.get('department') else '', v.get('name','').lower()
    ))  

    conn.close()
    
    # --- DEPARTMENT ANALYTICS FOR CAMPAIGN STATS ---
    dept_stats = {}
    # Initialize from victims
    for victim in victims:
        dept = victim.get('department') or 'Unknown'
        if dept not in dept_stats:
            dept_stats[dept] = {'total_victims': 0, 'conversions': 0}
        dept_stats[dept]['total_victims'] += 1

    # Count conversions
    for hit in hits:
        victim_email = hit['email']  # ← DEFINE THIS FIRST!
        victim_dept = 'Unknown'
        
        # Find department for this email
        for v in victims:
            if v['email'] == victim_email:
                victim_dept = v.get('department') or 'Unknown'
                break
        
        if victim_dept not in dept_stats:
            dept_stats[victim_dept] = {'total_victims': 0, 'conversions': 0}
        
        dept_stats[victim_dept]['conversions'] += 1

    # Build dept_list
    dept_list = []
    for dept, stats in dept_stats.items():
        total = stats.get('total_victims', 0)
        conversions = stats.get('conversions', 0)
    
        conversion_rate = round((conversions / total) * 100, 1) if total > 0 else 0.0
        dept_list.append({
            'name': dept,
            'total_victims': total,
            'conversions': conversions,
            'conversion_rate': conversion_rate
        })
    
    # Overall campaign stats
    total_victims = len(victims)
    total_conversions = len(hits)
    overall_conversion_rate = round((total_conversions / total_victims) * 100, 1) if total_victims > 0 else 0
    
    return render_template('stats.html', 
                         campaign=campaign, 
                         hits=hits, 
                         victims=victims,
                         dept_list=dept_list,
                         overall_conversion_rate=overall_conversion_rate,
                         total_victims=total_victims,
                         total_conversions=total_conversions)



@app.route('/campaign/<int:campaign_id>/delete', methods= ['POST'])
def delete_campaign_route(campaign_id) :
      """delete a campaign"""
      delete_campaign(int(campaign_id))
      flash(f'Campaign {campaign_id} deleted!', 'success')
      return redirect('/')


@app.route('/campaign/<int:campaign_id>/send' , methods=['POST'])
def send_campaign(campaign_id):
      success , message = send_campaign_emails(campaign_id)
      if success :
            flash(message, 'success')
      else:
            flash(f'Error: {message}', 'danger')
      return redirect(f'/campaign/{campaign_id}/stats')



@app.route('/campaign/<int:campaign_id>/add_victim', methods=['POST'])
def add_single_victim(campaign_id):
      email = request.form.get('email', '').strip()
      name = request.form.get('name', '').strip()
      department = request.form.get('department', '').strip()
      if department.isdigit():
        flash('Department must be a name (e.g., "IT"), not a number!', 'danger')
        return redirect(f'/campaign/{campaign_id}/stats')

        if not email:
            flash('Email is required!', 'danger')
        return redirect(f'/campaign/{campaign_id}/stats')  
      
      if not email:
        flash('Email is required!', 'danger')
        return redirect(f'/campaign/{campaign_id}/stats')

      results=add_victim(campaign_id=campaign_id , email=email , name=request.form.get('name','').strip(), department=request.form.get('departemnt','').strip())
      if results:
            flash(f'added victim : {email}', 'success')
      else:
           flash(f'Skipped (duplicate): {email}', 'warning')
    
      return redirect(f'/campaign/{campaign_id}/stats')
@app.route('/campaign/<int:campaign_id>/edit_victim/<int:victim_id>', methods=['POST'])
def edit_victim(campaign_id , victim_id):
      email = request.form.get('email', '').strip()
      name = request.form.get('name', '').strip()
      department = request.form.get('department', '').strip()
      
      if not email:
        flash('Email is required!', 'danger')
        return redirect(f'/campaign/{campaign_id}/stats')
      conn = get_db_connection()
      conn.execute('''
        UPDATE victims 
        SET email = ?, name = ?, department = ? 
        WHERE id = ? AND campaign_id = ?
                   ''',(email,name,department,victim_id,campaign_id))
      conn.commit()
      conn.close()
      flash('victim updated!', 'success')
      return redirect(f'/campaign/{campaign_id}/stats')

@app.route('/campaign/<int:campaign_id>/delete_victim/<int:victim_id>', methods=['POST'])
def delete_victim(campaign_id , victim_id):
     conn = get_db_connection()
     conn.execute('DELETE FROM victims WHERE id = ? AND campaign_id = ?', (victim_id,campaign_id))
     conn.commit()
     conn.close()
     flash('Victim deleted', 'info')
     return redirect (f'/campaign/{campaign_id}/stats')




@app.route('/campaign/<int:campaign_id>/export_pdf')
def export_campaign_pdf(campaign_id):
    """Generate and download PDF reports for a campaign"""
    campaign = get_campaign(campaign_id)
    if not campaign:
         return "campaign not found" , 404
    conn = get_db_connection()
    hits= conn.execute('''
        SELECT email, password, ip_address, timestamp
        FROM hits 
        WHERE campaign_id = ?
        ORDER BY timestamp ASC             
    ''',(campaign_id,)).fetchall()
    victims = get_victims(campaign_id)
    conn.close()

        # Sort victims by department
    victims.sort(key=lambda v: (
        v.get('department', '').lower() if v.get('department') else '',
        v.get('name', '').lower()
    ))


    dept_stats = {}
    for v in victims:
        dept = v.get('department') or 'Unknown'
        if dept not in dept_stats:
            dept_stats[dept] = {'total_victims': 0, 'conversions': 0}
        dept_stats[dept]['total_victims'] += 1  
    
    for hit in hits:
        victim_match = next((v for v in victims if v['email'] == hit['email']), None)
        dept = victim_match.get('department') if victim_match else 'Unknown'
        
        if dept not in dept_stats:
            dept_stats[dept] = {'total_victims': 0, 'conversions': 0}
        
        dept_stats[dept]['conversions'] += 1

    dept_list = []
    for dept, data in dept_stats.items():
        total = data['total_victims']      
        conversions = data['conversions']  
        rate = round((conversions / total) * 100, 1) if total > 0 else 0.0
        dept_list.append({
            'name': dept,
            'total_victims': total,
            'conversions': conversions,
            'conversion_rate': rate
        })
        
    
    total_victims = len(victims)
    total_conversions = len(hits)
    overall_rate = round((total_conversions / total_victims) * 100, 1) if total_victims > 0 else 0

   
   
    html= render_template(
        'report_pdf.html',
        campaign=campaign,
        dept_list=dept_list,
        hits=hits,
        overall_conversion_rate=overall_rate,
        total_victims=total_victims,
        total_conversions=total_conversions,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        )

    try :
         pdf= HTML(string=html).write_pdf()
    except OSError as e:
         return f"PDF generation failed : {str(e)}" , 500
    return Response(
         pdf, 
         mimetype='application/pdf',
         headers={
              'Content-Disposition': f'attachment; filename=phishforge_report_{campaign_id}.pdf'
         })

@app.route('/campaign/<int:campaign_id>/export_victims_csv')
def export_victims_csv(campaign_id):
    """Export victim list as CSV"""
    victims = get_victims(campaign_id)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Email', 'name', 'Department'])
    for v in victims:
         writer.writerow([
            v['email'],
            v.get('name', ''),
            v.get('department', '')
         ])
    return Response(
         output.getvalue(),
         mimetype="text/csv",
         headers={
            "Content-Disposition": f"attachment; filename=victims_campaign_{campaign_id}.csv"
        }
    )
@app.route('/campaign/<int:campaign_id>/export_hits_csv')
def export_hits_csv(campaign_id):
    """Export captured credentials as CSV"""
    conn = get_db_connection()
    hits =conn.execute('''
        SELECT email, password, ip_address, timestamp
        FROM hits 
        WHERE campaign_id = ?
        ORDER BY timestamp ASC
    ''', (campaign_id,)).fetchall()
    conn.close()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Email', 'Password', 'IP Address', 'Timestamp'])
    for hit in hits :
        writer.writerow([
            hit['email'],
            hit['password'],
            hit['ip_address'],
            hit['timestamp']
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=hits_campaign_{campaign_id}.csv"
        })


if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0' , port=8080)
