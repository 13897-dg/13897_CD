package enidh.cd.web;

import javax.swing.text.BadLocationException;

/**
 *
 * @author cgonc
 */
public class WebBowser {

    /**
     * @param args the command line arguments
     * @throws javax.swing.text.BadLocationException
     */
    public static void main(String args[]) throws BadLocationException {
        /* Create and display the form */
        java.awt.EventQueue.invokeLater(() -> {
            new SimpleBrowser().setVisible(true);
        });
    }
}
