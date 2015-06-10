import java.io.*;

/**
 * Created by tjc1575 on 6/10/15.
 */
public class Logger {
    private static final Object lock = new Object();
    private static PrintStream out;

    public static void setup() {
        out = System.out;
    }

    public static void setFile( String filename ) throws FileNotFoundException {
        out = new PrintStream(filename);
    }

    public static void print( String message ) {
        synchronized( lock ) {
            out.print(message);
        }
    }

    public static void println( String message ) {
        synchronized( lock ) {
            out.println(message);
        }
    }

    public static void close() {
        if( out != null ){
            out.close();
        }
    }

}
