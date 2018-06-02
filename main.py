import tornado.ioloop
import tornado.web
import image_processing as ip

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html")

class PhotoHandler(tornado.web.RequestHandler):
    def get(self):
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
        self.write(ip.encode_image_as_string(
            ip.find_image_angle_properties(img1, img2)))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/photo", PhotoHandler)
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()


