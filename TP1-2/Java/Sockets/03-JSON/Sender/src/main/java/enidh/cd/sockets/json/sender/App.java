package enidh.cd.sockets.json.sender;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper; 
import com.fasterxml.jackson.databind.ObjectWriter; 
import java.io.InputStream;
import java.io.OutputStream;

import java.net.Socket;

import java.util.Random;

/**
 *
 * @author cgonc
 */
public class App {
    private static final String DefaultHostName = "localhost";
    
    private static final int DefaultPort = 12350;
    
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
    
    public void run() {
        if (this.s != null) {
            try {
                Random rnd = new Random( System.currentTimeMillis() );
                
                MyListOfItems items = new MyListOfItems();
                for(int i=0; i<5; ++i) {
                    items.addItem( new MyItem( 10.0f + rnd.nextFloat( 20.0f) ) );
                }
                
                ObjectMapper mapper = new ObjectMapper();
                
                ObjectWriter ow = mapper.writer().withDefaultPrettyPrinter();
                
                String dataToSend = ow.writeValueAsString(items );
                
                System.out.printf( "Goint to send data:\n%s\n", dataToSend );
                
                OutputStream out = this.s.getOutputStream();
                out.write( dataToSend.getBytes() );
                
                InputStream in = this.s.getInputStream();
                byte[] responseRAW = new byte[ 1024 ];
                int numBytesRd = in.read(responseRAW );
                
                if ( numBytesRd>0 ) {
                    String responseAsString = new String( responseRAW, 0, numBytesRd );
                    
                    System.out.printf( "Response (RAW format):\n%s\n", responseAsString );
                    
                    MyItemResponse response = 
                            mapper.readValue(
                                    responseRAW, 
                                    MyItemResponse.class);
                    
                    System.out.printf( "Response:\n%s\n", response );
                }
            } catch (JsonProcessingException ex) {
                ex.printStackTrace( System.err );
            }
            catch (Exception e) {
                System.out.printf("Erro ao processar mensagens.\nDetalhes:\n");
                e.printStackTrace(System.err);
            }
        }

        System.out.printf("Cliente a terminar.\n");
    }
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        String host = (args.length>=1) ? args[0] : DefaultHostName; 
        int port = (args.length>=2) ? Integer.parseInt( args[1] ) : DefaultPort;

        App cli = new App(host, port );
        cli.run();
        
        System.out.println("Função main do cliente a terminar...");
    }
}
