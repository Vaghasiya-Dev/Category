from app import app as application

# Vercel expects the app to be named 'app' or to export it
app = application

if __name__ == "__main__":
    app.run()
