package enidh.cd.sockets.calc.server;

import java.util.ArrayList;
import java.util.List;

public class ComplexRequestList {
    public List<ComplexOperation> operations = new ArrayList<>();
    
    public ComplexRequestList() {}
    
    public void addOperation(ComplexOperation op) {
        this.operations.add(op);
    }
}
