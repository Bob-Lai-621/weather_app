import SwiftUI


struct ContentView: View {
    @State private var city: String = ""
    @State private var weather: String = "Enter a city to check the weather"
    
    let backgroundGradient = LinearGradient(
        colors: [Color.blue.opacity(0.3), Color.blue.opacity(0.1)],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    struct WeatherResponse: Codable {
        let current_temp: Double
        let current_desc: String
        let city: String
        
        // If you want to use different property names in Swift
        enum CodingKeys: String, CodingKey {
            case current_temp
            case current_desc
            case city
        }
    }
    
    func fetchWeather() {
        guard let url = URL(string: "http://127.0.0.1:8000/api/weather/\(city)") else {
            weather = "Invalid URL"
            return
        }

        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    weather = "Error: \(error.localizedDescription)"
                }
                return
            }
            
            if let data = data {
                // For debugging
                if let jsonString = String(data: data, encoding: .utf8) {
                    print("Received JSON:", jsonString)
                }
                
                if let decodedResponse = try? JSONDecoder().decode(WeatherResponse.self, from: data) {
                    DispatchQueue.main.async {
                        weather = "🌡️ \(decodedResponse.current_temp)°C - \(decodedResponse.current_desc.capitalized)"
                    }
                    return
                } else {
                    DispatchQueue.main.async {
                        weather = "Failed to decode response"
                    }
                }
            }
            
            DispatchQueue.main.async {
                weather = "⚠️ Failed to fetch weather"
            }
        }.resume()
    }
    
    var body: some View {
        ZStack {
            // Background gradient
            backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 20) {
                // Weather icon and title
                HStack {
                    Image(systemName: "sun.max.fill")
                        .font(.system(size: 40))
                        .foregroundColor(.yellow)
                        .shadow(radius: 2)
                    
                    Text("Weather App")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.blue)
                }
                .padding()
                .shadow(radius: 2)
                
                // Search field with icon
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.gray)
                    TextField("Enter City", text: $city)
                }
                .padding()
                .background(Color.white)
                .cornerRadius(15)
                .padding(.horizontal, 40)
                .shadow(radius: 2)
                
                // Search button with icon
                Button(action: {
                    fetchWeather()
                }) {
                    HStack {
                        Image(systemName: "location.magnifyingglass")
                            .font(.system(size: 20))
                        Text("Get Weather")
                            .fontWeight(.semibold)
                    }
                    .frame(minWidth: 200)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(15)
                    .shadow(radius: 3)
                }
                
                // Weather display card
                VStack {
                    if weather == "Fetching data..." {
                        Image(systemName: "arrow.clockwise")
                            .font(.system(size: 30))
                            .foregroundColor(.blue)
                    } else {
                        Image(systemName: "cloud.sun.fill")
                            .font(.system(size: 50))
                            .foregroundColor(.blue)
                    }
                    
                    Text(weather)
                        .font(.system(size: 18))
                        .multilineTextAlignment(.center)
                }
                .padding()
                .frame(minHeight: 150)
                .frame(maxWidth: .infinity)
                .background(Color.white)
                .cornerRadius(15)
                .shadow(radius: 3)
                .padding(.horizontal)
            }
            .padding()
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
