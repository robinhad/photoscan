import tornado.ioloop
import tornado.web
import image_processing as ip

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html")

class PhotoHandler(tornado.web.RequestHandler):
    def post(self):
        '''API method for saving coordinates in database'''
        '''request.form['id']
        request.form['image']  # TODO: try request files?
        request.form['longitude']
        request.form['latitude']
        request.form['altitude']
        request.form['anglex']  # Shear
        request.form['angley']  # Theta  '''
        data_json = self.request.body
        #img1 = str.encode(str(request.args.get('img1').replace(" ", "+")))
        img1 = ip.decode_image_from_string(data_json)
        #ip.cv2.imwrite("received.jpg", img1)
        img2 = ip.cv2.imread("test.jpg", 0)
        img3 = ip.find_image_angle_properties(img1, img2)
        ip.cv2.imwrite("haha.jpg", img3)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/photo", PhotoHandler)
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
tornado.ioloop.IOLoop.current().start()