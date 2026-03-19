package enidh.cd.sockets.json.sender;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 *
 * @author cgonc
 */
public class MyItemResponse {
    @JsonProperty("Temperature average")
    private float temperatureAverage;
    
    public float getTemperatureAverage() {
        return this.temperatureAverage;
    }

    public void setTemperatureAverage(float temperatureAverage) {
        this.temperatureAverage = temperatureAverage;
    }
    
    public MyItemResponse() {
        this( 0.0f );
    }
    
    public MyItemResponse(float temperatureAverage) {
        this.temperatureAverage = temperatureAverage;
    }
    
    @Override
    public String toString() {
        return String.format( "Temperature average: %4.2f", this.temperatureAverage );
    }
}
