package enidh.cd.sockets.calc.server;

public class ComplexOperation {
    public int r1;
    public int i1;
    public int r2;
    public int i2;
    public String oper;

    public ComplexOperation() {}
    
    public ComplexOperation(int r1, int i1, int r2, int i2, String oper) {
        this.r1 = r1;
        this.i1 = i1;
        this.r2 = r2;
        this.i2 = i2;
        this.oper = oper;
    }
}
