/*
    Filename: Logger.java
    Author: Taylor Carpenter <tjc1575@rit.ed>

    Handles the logging for the application. If a file is set, all logging
    is written out to the file, otherwise it writes out to standard out.
    Logging is synchronized to allow for access from multiple threads.
 */

import java.io.FileNotFoundException;
import java.io.PrintStream;

public class Logger {
    private static final Object lock = new Object();
    private static PrintStream out;

    /*
        Set the initial output to be standard out.
     */
    public static void setup() {
        out = System.out;
    }

    /*
        Set the output stream to the given file.
     */
    public static void setFile( String filename ) throws FileNotFoundException {
        out = new PrintStream(filename);
    }

    /*
        Perform a synchronized print to the output stream, no newline.
     */
    public static void print( String message ) {
        synchronized( lock ) {
            out.print(message);
        }
    }

    /*
        Perform a synchronized println to the output stream.
     */
    public static void println( String message ) {
        synchronized( lock ) {
            out.println(message);
        }
    }

    /*
        Try to close the output stream to free resources.
     */
    public static void close() {
        if( out != null ){
            out.close();
        }
    }

}
