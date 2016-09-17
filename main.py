import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("front.html", blogposts=blogposts)

class PostPage(Handler):
    def render_front(self, title="", body="", error=""):
        self.render("newpost.html", title=title, body=body, error=error)

    def get(self):
        self.render_front()
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = BlogPost(title = title, body = body)
            key = post.put()

            self.redirect("/blog/%s" % key.id())
        else:
            error = "We need a title & body!"
            self.render_front(title, body, error)

class BlogPage(Handler):
    def get(self):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC")
        self.render("blog.html", blogposts=blogposts)

class PermaPage(Handler):
    def get(self, post_id):
        post = BlogPost.get_by_id(int(post_id))
        self.render("blog.html", blogposts = [post])

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', PostPage),
    ('/blog', BlogPage),
    ('/blog/(\d+)', PermaPage)
], debug=True)
