import oscP5.*;
import netP5.*;

Table datos;
int currentRow = 0;
int delayFrames = 60;
OscP5 osc;
NetAddress pd;
ArrayList<Particula> particulas = new ArrayList<Particula>();

void setup() {
  size(900, 700);
  
  // Validar carga del archivo CSV
  try {
    datos = loadTable("Stress-Lysis.csv", "header");
    if (datos.getRowCount() == 0) {
      println("ERROR: El archivo CSV está vacío");
      exit();
    }
  } catch (Exception e) {
    println("ERROR: No se pudo cargar el archivo CSV");
    println(e.getMessage());
    exit();
    return;
  }
  
  // Abrimos OSC en el puerto 12000 (Processing)
  osc = new OscP5(this, 12000);
  // Pure Data escucha en el puerto 11111
  pd = new NetAddress("127.0.0.1", 11111);
  frameRate(60);
}

void draw() {
  background(255);
  
  // Título
  fill(0);
  textSize(22);
  text("Proyecto 5", 20, 40);
  
  // Leyenda en la parte superior
  drawLegend();
  
  // Actualizar y crear nuevas partículas
  if (frameCount % delayFrames == 0) {
    if (currentRow < datos.getRowCount()) {
      crearParticulas(currentRow);
      enviarFilaOSC(currentRow);
      currentRow++;
    } else {
      currentRow = 0;
    }
  }
  
  // Actualizar y dibujar partículas
  for (int i = particulas.size() - 1; i >= 0; i--) {
    Particula p = particulas.get(i);
    p.update();
    p.display();
    if (p.estaFuera()) {
      particulas.remove(i);
    }
  }
}

// ==============================
//   CREAR PARTÍCULAS CON DATOS
// ==============================
void crearParticulas(int dataIndex) {
  try {
    TableRow row = datos.getRow(dataIndex);
    
    float humidity = row.getFloat("Humidity");
    float temperature = row.getFloat("Temperature");
    float stress = row.getFloat("Stress_Level");
    
    // Crear partícula de HUMEDAD (azul, velocidad varía)
    particulas.add(new Particula(250, 100, humidity, temperature, stress, "humidity"));
    
    // Crear partícula de TEMPERATURA (color varía según temperatura)
    particulas.add(new Particula(450, 100, humidity, temperature, stress, "temperature"));
    
    // Crear partícula de STRESS (rojo, tamaño varía)
    particulas.add(new Particula(680, 100, humidity, temperature, stress, "stress"));
    
  } catch (Exception e) {
    println("Error creando partículas: " + e.getMessage());
  }
}

// ==============================
//   CLASE PARTÍCULA
// ==============================
class Particula {
  float x, y;
  float vx, vy;
  float humidity, temperature, stress;
  String tipo;
  float alpha = 255;
  
  Particula(float startX, float startY, float h, float t, float st, String t_) {
    x = startX;
    y = startY;
    humidity = h;
    temperature = t;
    stress = st;
    tipo = t_;
    
    // Movimiento hacia abajo sin variación horizontal (columnas rectas)
    vx = 0;
    
    if (tipo.equals("humidity")) {
      // HUMEDAD: velocidad varía según humedad
      // Mucha humedad = rápido, poca humedad = lento
      vy = map(humidity, 0, 100, 1, 6);
    } else {
      // TEMPERATURA y STRESS: velocidad normal
      vy = 3;
    }
  }
  
  void update() {
    x += vx;
    y += vy;
  }
  
  void display() {
    noStroke();
    
    if (tipo.equals("humidity")) {
      // HUMEDAD: azul, tamaño fijo, velocidad varía
      fill(0, 150, 255, alpha);
      ellipse(x, y, 35, 35);
      
      // Texto valor
      fill(0, alpha);
      textSize(10);
      textAlign(CENTER);
      text(nf(humidity, 0, 1), x, y + 40);
      
    } else if (tipo.equals("temperature")) {
      // TEMPERATURA: color varía (morado frío -> rojo caliente), tamaño fijo
      // Mapear temperatura a color
      float r = map(temperature, 60, 120, 100, 255);
      float b = map(temperature, 60, 120, 255, 0);
      fill(r, 0, b, alpha);
      ellipse(x, y, 35, 35);
      
      // Texto valor
      fill(0, alpha);
      textSize(10);
      textAlign(CENTER);
      text(nf(temperature, 0, 1), x, y + 40);
      
    } else if (tipo.equals("stress")) {
      // STRESS: rojo, tamaño varía según nivel de estrés
      // Mucho estrés = grande, poco estrés = pequeño
      float size = map(stress, 0, 3, 15, 50);
      fill(255, 100, 100, alpha);
      ellipse(x, y, size, size);
      
      // Texto valor
      fill(0, alpha);
      textSize(10);
      textAlign(CENTER);
      text(int(stress), x, y + size/2 + 15);
    }
    
    textAlign(LEFT);
  }
  
  boolean estaFuera() {
    return y > height + 50;
  }
}

// ==============================
//   FUNCIÓN QUE ENVÍA A PURE DATA
// ==============================
void enviarFilaOSC(int i) {
    TableRow row = datos.getRow(i);
    
    float humidity = row.getFloat("Humidity");
    float temperature = row.getFloat("Temperature");
    float stress = row.getFloat("Stress_Level");
    
    // ▪ Humidity
    OscMessage m1 = new OscMessage("/humidity");
    m1.add(humidity);
    osc.send(m1, pd);
    
    // ▪ Temperature
    OscMessage m2 = new OscMessage("/temperature");
    m2.add(temperature);
    osc.send(m2, pd);
    
    // ▪ Stress Level
    OscMessage m3 = new OscMessage("/stress");
    m3.add(stress);
    osc.send(m3, pd);
    
    println("Enviado fila " + (i + 1) + " a Pure Data");
    

}

// ==============================
//         LEYENDA
// ==============================
void drawLegend() {
  textSize(14);
  fill(0, 150, 255);
  ellipse(250, 80, 20, 20);
  fill(0); 
  text("Humidity", 280, 85);
  
  fill(150, 0, 150);
  ellipse(450, 80, 20, 20);
  fill(0); 
  text("Temperature", 480, 85);
  
  fill(255, 100, 100);
  ellipse(680, 80, 20, 20);
  fill(0); 
  text("Stress", 710, 85);
}
