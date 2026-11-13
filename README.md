# Deepfake Detection Tool Using Machine Learning

An advanced, real-time image authenticity verification platform that decomposes and analyzes images to determine if an uploaded image is **real** or an **AI-generated deepfake / synthetic manipulation**.

Built with **Flask**, **OpenCV**, **NumPy**, and classical image forensic techniques.

---

## 🔬 Detection Methodology

The detection engine runs 5 forensic layers in parallel to inspect distinct artifact classes:

1. **Error Level Analysis (ELA)**: Re-saves the image under a controlled quantization table and measures differential reconstruction error. Composited, edited, or generative regions show marked spikes in residual error.
2. **Noise Pattern Inconsistency**: Real digital cameras generate uniform CMOS sensor noise. Generative inpainting and diffusion smoothing break this local variance.
3. **Spectral FFT Artifacts**: 2D Fast Fourier Transform exposes periodic grid artifacts left in the high-frequency spectrum by convolutional neural network decoders and GAN generators.
4. **Seam & Boundary Detection**: Sobel luminance gradient filtering isolates edge step-discontinuities and unnatural boundary feathering common in face-swapping algorithms.
5. **JPEG Ghost Analysis**: Pinpoints multi-generation quantization ghosts produced when pasting elements from sources with differing JPEG compression histories.

---

## 👥 Credits & Contributors

- **Sai Kiran** ([@Saikiran200104](https://github.com/Saikiran200104)) — Creator of the original `deepfakedemo` foundation and early prototypes.
- **Subhang Avula** ([@lyro-pyro](https://github.com/lyro-pyro)) — Full platform rebuild, forensic algorithms implementation, UI/UX redesign, and deployment.

---

## 🚀 Getting Started

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lyro-pyro/Deepfake-Detection-Tool-Using-Machine-Learning.git
   cd Deepfake-Detection-Tool-Using-Machine-Learning
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access in browser**:
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🌐 Deployment

The application is pre-configured for serverless deployment on **Vercel** via `vercel.json` and `api/index.py`.

Deploy using the Vercel CLI:
```bash
vercel --prod
```
