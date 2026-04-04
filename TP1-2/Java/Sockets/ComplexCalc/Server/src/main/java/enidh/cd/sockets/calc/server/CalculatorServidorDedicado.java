package enidh.cd.sockets.calc.server;

/**
 *
 * @author cgonc
 */
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;

/**
 *
 * @author cgonc
 */
public class CalculatorServidorDedicado implements Runnable {

    private final Socket s;

    /**
     * @param s the socket to the client
     */
    public CalculatorServidorDedicado(Socket s) {
        this.s = s;
        
        System.out.println("Servidor dedicado criado" );
    }

    @Override
    public void run() {
        System.out.printf("Servidor dedicado ativo no endereço %s no porto %d.\n", this.s.getInetAddress().toString(), this.s.getLocalPort() );

        InputStream in = null;
        OutputStream out = null;
        
        try {
            in = this.s.getInputStream();
            out = this.s.getOutputStream();

            byte[] requestRAW = new byte[4096];
            int numBytesRd = in.read(requestRAW);
            
            if (numBytesRd > 0) {
                ObjectMapper mapper = new ObjectMapper();
                ComplexRequestList requests = mapper.readValue(requestRAW, ComplexRequestList.class);

                ComplexResponseList responses = new ComplexResponseList();
                
                for (ComplexOperation op : requests.operations) {
                    System.out.printf( "Op: (%d + %di) %s (%d + %di)\n", op.r1, op.i1, op.oper, op.r2, op.i2 );
                    
                    ComplexResult res = new ComplexResult();
                    
                    switch ( op.oper ) {
                        case "+":
                            res.rRes = op.r1 + op.r2;
                            res.iRes = op.i1 + op.i2;
                            break;
                        
                        case "-":
                            res.rRes = op.r1 - op.r2;
                            res.iRes = op.i1 - op.i2;
                            break;
                        
                        case "*":
                            res.rRes = (op.r1 * op.r2) - (op.i1 * op.i2);
                            res.iRes = (op.r1 * op.i2) + (op.i1 * op.r2);
                            break;
                        
                        default:
                            System.out.println("Invalid operation.");
                            break;
                    }
                    responses.results.add(res);
                }

                ObjectWriter ow = mapper.writer().withDefaultPrettyPrinter();
                String dataToSend = ow.writeValueAsString(responses);

                out.write(dataToSend.getBytes());
                out.flush();
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
