from app import db, Posts

posts = Posts.query.all()
for post in posts:
    if post.upvotes is None:
        post.upvotes = 0
    if post.downvotes is None:
        post.downvotes = 0
    db.session.commit()