package enidh.cd.sockets.json.sender;

import java.sql.Timestamp;

/**
 *
 * @author cgonc
 */
public class MyItem {
    private String timestamp;
    
    public String getTimestamp() {
        return this.timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
    
    private float temperature;

    public float getTemperature() {
        return this.temperature;
    }

    public void setTemperature(float temperature) {
        this.temperature = temperature;
    }
    
    public MyItem() {
        this( (new Timestamp(System.currentTimeMillis())).toString(), -1);
    }
    
    public MyItem(float temperature) {
        this( (new Timestamp(System.currentTimeMillis())).toString(), temperature);
    }
    
    public MyItem(String timestamp, float temperature ) {
        this.timestamp = timestamp;
        this.temperature = temperature;
    }
}
