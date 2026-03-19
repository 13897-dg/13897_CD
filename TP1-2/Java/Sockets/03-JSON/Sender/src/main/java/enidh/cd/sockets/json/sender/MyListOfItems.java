package enidh.cd.sockets.json.sender;

import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author cgonc
 */
public class MyListOfItems {
    private List<MyItem> items;

    public List<MyItem> getItems() {
        return items;
    }

    public void setItems(List<MyItem> items) {
        this.items = items;
    }
    
    public void addItem(MyItem item) {
        this.items.add(item);
    }
    
    public MyListOfItems() {
        this.items = new ArrayList<>();
    }
}
