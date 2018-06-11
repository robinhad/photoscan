import tornado.ioloop
import tornado.web
import image_processing as ip
import json

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html")

class PhotoHandler(tornado.web.RequestHandler):
    def post(self):
        data_json = self.request.body

        img1 = ip.cv2.imread("./images/test.jpg", 0)
        img2 = ip.decode_image_from_string(data_json)
        img3, components = ip.find_image_angle_properties(img1, img2)

        ip.cv2.imwrite("./images/result.jpg", img3)

        theta = components[1]
        shear = components[3]
        angles = dict()

        angles["translationx"] = components[0][0] 
        angles["translationy"] = components[0][1]
        angles["scalex"] = components[2][0] 
        angles["scaley"] = components[2][1]
        angles["theta"] = ip.toRadians(theta)
        angles["shear"] = ip.toRadians(shear)

        self.write(json.dumps(angles))#ip.encode_image_as_string(img3)

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/photo", PhotoHandler),
        (r'/(result\.jpg)', MyStaticFileHandler, {'path': "./images"}),
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
tornado.ioloop.IOLoop.current().start()