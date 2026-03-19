package enidh.cd.utils;

import java.awt.Component;

import javax.swing.JOptionPane;

public class ExceptionsUtils {

    public static String getStackTrace(Throwable t, int depth) {
        StringBuilder sb = new StringBuilder("Detalhes:\n\n");

        for (StackTraceElement elem : t.getStackTrace()) {
            if (depth < 0) {
                break;
            }

            sb.append(elem.toString());
            sb.append("\n");
            --depth;
        }

        return sb.toString();
    }

    public static void showException(Component parent, Throwable t, String title) {
        JOptionPane.showMessageDialog(
                parent,
                getStackTrace(t, 10),
                title,
                JOptionPane.ERROR_MESSAGE);
    }
}
