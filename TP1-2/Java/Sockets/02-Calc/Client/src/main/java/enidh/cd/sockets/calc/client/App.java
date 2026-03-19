package enidh.cd.sockets.calc.client;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;

/**
 *
 * @author cgonc
 */
public class App extends Thread {
    
    private static final String DefaultHostName = "localhost";
    
    private static final int DefaultPort = 12345;
    
    private Socket s;
    
    public App(String host, int port) {
        try {
            this.s = new Socket(host, port);
 
            System.out.printf("Ligação estabelecida (%s).\n", this.s.toString());
        } catch (Exception e) {
            this.s = null;

            System.out.printf("Não foi possível estabelecer ligação com o servidor (%s) no porto pretendio (%d)\nDetalhes:\n", host, port);
            e.printStackTrace(System.err);
        }
    }
    
    private void sendArgs(DataOutputStream out, int op1, int op2, byte oper) throws IOException {
        out.writeInt( op1 );
        out.writeInt( op2 );
        out.writeByte( oper );
        
        out.flush();
    }
    
    private void showResponse(int op1, char oper, int op2, int result) {
        System.out.printf( "%d %c %d = %d\n", op1, oper, op2, result );
    }
    
    @Override
    public void run() {
        if (this.s != null) {
            try {
                DataOutputStream out = new DataOutputStream( this.s.getOutputStream() );
                
                int op1, op2;
                char oper1, oper2, oper3, oper4;
                
                sendArgs( out, op1=5, op2=2, (byte)(oper1 = '+') );               
                sendArgs( out, op1, op2, (byte)(oper2 = '-') );
                sendArgs( out, op1, op2, (byte)(oper3 = '*') );
                sendArgs( out, op1, op2, (byte)(oper4 = '/') );

                DataInputStream in = new DataInputStream( this.s.getInputStream() );
                
                showResponse( op1, oper1, op2, in.readInt() );
                showResponse( op1, oper2, op2, in.readInt() );
                showResponse( op1, oper3, op2, in.readInt() );
                showResponse( op1, oper4, op2, in.readInt() );

                out.close();
                in.close();
                s.close();
            } catch (Exception e) {
                System.out.printf("Erro ao processar mensagens.\nDetalhes:\n");
                e.printStackTrace(System.err);
            }
        }

        System.out.printf("Cliente a terminar.\n");
    }

    /**
     * @param args the command line arguments
     *
     * args[0] is the host name (string) 
     * args[1] is the port number (integer)
     */
    public static void main(String[] args) {
        String host = (args.length>=1) ? args[0] : DefaultHostName; 
        int port = (args.length>=2) ? Integer.parseInt( args[1] ) : DefaultPort;

        App cli = new App(host, port );
        cli.start();

        System.out.println("Função main do cliente a terminar...");
    }
    
}
