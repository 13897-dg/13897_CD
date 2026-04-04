package enidh.cd.sockets.calc.server;

/**
 *
 * @author cgonc
 */
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.Socket;

/**
 *
 * @author cgonc
 */
public class HelloServidorDedicado extends Thread {

    private final Socket s;

    /**
     * @param s the socket to the client
     */
    public HelloServidorDedicado(Socket s) {
        this.s = s;
        
        System.out.println("Servidor dedicado criado" );
    }

    @Override
    public void run() {
        System.out.printf("Servidor dedicado ativo no endereço %s no porto %d.\n", this.s.getInetAddress().toString(), this.s.getLocalPort() );

        DataInputStream in = null;
        DataOutputStream out = null;
        
        try {
            // ordem inversa do cliente
            in = new DataInputStream( this.s.getInputStream() );
            out = new DataOutputStream( this.s.getOutputStream() );

            for( ; ; ) {
                int op1 = in.readInt();
                int op2 = in.readInt();
                byte oper = in.readByte();
                
                System.out.printf( "%d %c %d\n", op1, (char)oper, op2 );
                
                int res;
                
                switch ( oper ) {
                    case '+':
                        res = op1 + op2;        
                        break;
                    
                    case '-':
                        res = op1 - op2;
                        break;
                    
                    case '*':
                        res = op1 * op2;
                        break;
                    
                    case '/':
                        res = op1 / op2;
                        break;
                    
                    default:
                            res = -1;
                        break;
                }
                
                out.writeInt( res );
            }
        }
        catch (java.io.EOFException ioEx) {
            System.out.println( "Ligação fechada." );
        }
        catch (Exception ex) {
            System.err.printf( "Erro no servidor dedicado!\nDetalhes:\n" );
            ex.printStackTrace( System.err );
        }
        finally {
            try {
                if ( in!=null ) {
                    in.close();
                }
                if ( out!=null ) {
                    out.close();
                }
                this.s.close();
            }
            catch (Exception ex) {
                System.err.printf( "Erro ao terminar servidor dedicado!\nDetalhes:\n" );
                ex.printStackTrace( System.err );
            }
        }

        System.out.printf("Servidor dedicado a terminar.\n");
    }
}
