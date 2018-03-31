from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    '''Main page in application, used for SPA serving'''
    name = "Default"
    return render_template('index.html', name=name)


#@app.route('/api/photos/<int:count>')
@app.route('/api/photos/')
def get_photos():
    '''API method for obtaining photos from site'''
    count = 10
    return 'You get {0} photos'.format(str(count))


@app.route('/api/photo/', methods=['POST'])
def save_photo_parameters():
    '''API method for saving coordinates in database'''
    request.form['id']
    request.form['image']  # TODO: try request files?
    request.form['longitude']
    request.form['latitude']
    request.form['altitude']
    request.form['anglex']  # Shear
    request.form['angley']  # Theta
    
    return 'Post'
