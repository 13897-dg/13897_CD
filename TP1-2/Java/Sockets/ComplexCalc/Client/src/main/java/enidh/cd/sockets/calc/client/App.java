package enidh.cd.sockets.calc.client;

import java.io.InputStream;
import java.io.OutputStream;
import java.io.IOException;
import java.net.Socket;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;

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
    private void showResponse(ComplexOperation op, ComplexResult res) {
        System.out.printf( "(%d + %di) %s (%d + %di) = %d + %di\n", op.r1, op.i1, op.oper, op.r2, op.i2, res.rRes, res.iRes );
    }
    
    @Override
    public void run() {
        if (this.s != null) {
            try {
                int r1 = 5, i1 = 2;
                int r2 = 3, i2 = 4;
                
                ComplexRequestList requests = new ComplexRequestList();
                requests.addOperation(new ComplexOperation(r1, i1, r2, i2, "+"));
                requests.addOperation(new ComplexOperation(r1, i1, r2, i2, "-"));
                requests.addOperation(new ComplexOperation(r1, i1, r2, i2, "*"));

                ObjectMapper mapper = new ObjectMapper();
                ObjectWriter ow = mapper.writer().withDefaultPrettyPrinter();
                String dataToSend = ow.writeValueAsString(requests);

                System.out.printf("Going to send data:\n%s\n", dataToSend);

                OutputStream out = this.s.getOutputStream();
                out.write(dataToSend.getBytes());
                out.flush();

                InputStream in = this.s.getInputStream();
                byte[] responseRAW = new byte[4096];
                int numBytesRd = in.read(responseRAW);

                if (numBytesRd > 0) {
                    String responseAsString = new String(responseRAW, 0, numBytesRd);
                    System.out.printf("Response (RAW format):\n%s\n", responseAsString);

                    ComplexResponseList responseList = mapper.readValue(responseRAW, ComplexResponseList.class);

                    for (int i = 0; i < requests.operations.size(); i++) {
                        showResponse(requests.operations.get(i), responseList.results.get(i));
                    }
                }

                out.close();
                in.close();
                s.close();
            } catch (JsonProcessingException ex) {
                ex.printStackTrace(System.err);
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
