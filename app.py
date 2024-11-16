from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Advanced Deepfake Detection</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet"/>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet"/>
        <style>
            /* Reset */
            * { margin: 0; padding: 0; box-sizing: border-box; }

            /* Body */
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #0c0e16;
                color: #f0f1f6;
                line-height: 1.6;
                padding: 0 20px;
            }

            /* Header */
            .navbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 20px 0;
                background-color: #0c0e16;
            }

            .navbar img {
                height: 50px;
            }

            .navbar a {
                color: #f0f1f6;
                margin-left: 20px;
                text-decoration: none;
                font-weight: 500;
            }

            /* Hero Section */
            .hero {
                text-align: center;
                padding: 100px 20px;
                background: linear-gradient(135deg, #1f2230, #0c0e16);
                color: #ffffff;
            }

            .hero h1 {
                font-size: 2.8rem;
                font-weight: 700;
                margin-bottom: 15px;
            }

            .hero p {
                font-size: 1.2rem;
                max-width: 600px;
                margin: 20px auto;
            }

            .hero .btn-primary, .hero .btn-secondary {
                display: inline-block;
                padding: 12px 25px;
                border-radius: 5px;
                text-decoration: none;
                font-weight: 500;
                margin-top: 20px;
            }

            .hero .btn-primary {
                background-color: #e94560;
                color: #ffffff;
            }

            .hero .btn-secondary {
                background-color: transparent;
                border: 1px solid #e94560;
                color: #e94560;
                margin-left: 10px;
            }

            /* Features Section */
            .features {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 40px;
                margin: 50px 0;
            }

            .features .feature {
                background-color: #1e293b;
                padding: 30px;
                border-radius: 8px;
            }

            .features .feature h2 {
                font-size: 1.5rem;
                color: #e94560;
                margin-bottom: 10px;
            }

            .features .feature p {
                color: #d1d1d1;
                font-size: 1rem;
            }

            /* Footer */
            footer {
                text-align: center;
                padding: 20px 0;
                font-size: 0.9rem;
                color: #888;
                background-color: #0c0e16;
            }
        </style>
    </head>
    <body>

        <!-- Navbar -->
        <div class="navbar">
            <img src="https://storage.googleapis.com/a1aa/image/BSJne7MKKLzzTS6DNd9dCTdFT0D8dLwA8VxSyhQZB1j7CI4JA.jpg" alt="Blackbox AI Logo">
            <div>
                <a href="#">Overview</a>
                <a href="#">Features</a>
                <a href="#">Contact</a>
            </div>
        </div>

        <!-- Hero Section -->
        <section class="hero">
            <h1>Revolutionizing Deepfake Detection</h1>
            <p>Experience the future of cybersecurity with Blackbox AI’s cutting-edge technology, designed to detect and combat deepfakes in real-time.</p>
            <a href="/subhang" class="btn-primary">Get Started</a>
            <a href="#" class="btn-secondary">Learn More</a>
        </section>

        <!-- Features Section -->
        <section class="features">
            <div class="feature">
                <h2>Advanced Deepfake Detection</h2>
                <p>Utilizes state-of-the-art machine learning to accurately detect manipulated media, safeguarding authenticity in digital content.</p>
            </div>
            <div class="feature">
                <h2>Real-Time Analysis</h2>
                <p>Process and identify deepfakes in real-time, providing immediate alerts and detailed analysis for faster response.</p>
            </div>
            <div class="feature">
                <h2>Scalable Solutions</h2>
                <p>From small businesses to large enterprises, Blackbox AI adapts to your needs, making it the ideal choice for any organization.</p>
            </div>
            <div class="feature">
                <h2>Protect Digital Integrity</h2>
                <p>Enhance trust in media by ensuring the legitimacy of audio, video, and images shared online.</p>
            </div>
        </section>

    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)
