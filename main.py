from flask import Flask, request, render_template
import image_processing as ip
app = Flask(__name__)


@app.route('/')
def index():
    '''Main page in application, used for SPA serving'''
    name = "Default"
    return render_template('index.html', name=name)


@app.route('/api/photos/')
def get_photos():
    '''API method for obtaining photos from site'''
    count = 10
    return 'You get {0} photos'.format(str(count))


@app.route('/api/photo/', methods=['GET'])
def save_photo_parameters():
    '''API method for saving coordinates in database'''
    '''request.form['id']
    request.form['image']  # TODO: try request files?
    request.form['longitude']
    request.form['latitude']
    request.form['altitude']
    request.form['anglex']  # Shear
    request.form['angley']  # Theta  '''

    img1 = str.encode(str(request.args.get('img1').replace(" ", "+")))
    img2 = str.encode(str(request.args.get('img2').replace(" ", "+")))
    img1 = ip.decode_image_from_string(img1)
    img2 = ip.decode_image_from_string(img2)
    return ip.encode_image_as_string(
        ip.find_image_angle_properties(img1, img2))
