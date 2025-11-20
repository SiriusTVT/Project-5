# Data Sonification and Visualization  
### Sistemas de Interacción – Miniproyecto 5  

🎥 **Demo Video:**  
[Click here to watch the project demonstration](PON_AQUI_EL_LINK_DEL_VIDEO)

**Authors:**  
- David Felipe Hurtado Marroquín  
- Juan David Troncoso  

---

## 📌 Project Description

This project is a data sonification and visualization system built using **Processing** and **Pure Data (PD)**.  
We selected a public dataset and used Processing to read the data, visualize it dynamically, and send the values to Pure Data through the OSC protocol. As the data changes, both the visual elements and the audio respond in real time.

The objective is to create a synchronized experience where the dataset influences the graphical behavior and generates sounds that reflect variations in humidity, temperature, and stress values.

---

## 🎧 Pure Data Patch

Our Pure Data patch receives OSC messages on port **11111** and processes three parameters:

- **humidity**  
- **temperature**  
- **stress**

Each parameter controls a different sound generator:

1. **Temperature → Sine Oscillators (660 Hz and 880 Hz)**  
   Produces clean tones whose amplitude changes depending on temperature.

2. **Humidity → Noise + Filter System**  
   A noise source is passed through low-pass and high-pass filters (`lop~`, `hip~`) creating a textured sound that varies with humidity.

3. **Stress → Phasor-based Tone + 1100 Hz Oscillator**  
   Generates cyclic and bright tones that reflect stress values.

## 🖥️ Processing Sketch

Our Processing sketch:

- Reads the dataset sequentially  
- Visualizes the values using shapes and colors  
- Sends humidity, temperature, and stress values to Pure Data using OSC  
- Updates the visuals and audio in real time  
- Allows interaction once all the data has been displayed  

This creates a direct connection between the visual and auditory behavior.

---

## 🧠 Justification

We designed the system this way to create a **clear mapping** between the dataset and the audiovisual output:

- Each variable controls a different sound engine, making the sonification easy to distinguish  
- Combining oscillators, noise, and filters allows expressive changes in the sound  
- Using OSC ensures **real-time communication** between Processing and Pure Data  
- The visuals and audio evolve together, helping the user understand the data through multiple senses  

This approach results in an intuitive, interactive, and meaningful data exploration experience.

---
