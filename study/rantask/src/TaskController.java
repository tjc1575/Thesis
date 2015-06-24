import javafx.application.Platform;

import java.time.LocalDateTime;
import java.util.Random;

/**
 * Created by tjc1575 on 6/6/15.
 */
public class TaskController implements Runnable{
    private static final Object lock = new Object();
    private Random ran;
    private SoundGenerator gen;
    private int steps = 0;

    private int[] counts;
    private int[] desired;
    private int[] toneCount;

    private int totalTone = 0;
    private int totalPress = 0;
    private int correct = 0;
    private int falsePos = 0;

    private int lastTone;
    private int status;

    private boolean cont;


    public TaskController( int low, int medium, int high, int time ) {
        int newLow = low == 0 ? -1 : low;
        int newMed = medium == 0 ? -1 : medium;
        int newHigh = high == 0 ? -1 : high;

        counts = new int[] {0,0,0};
        desired = new int[] {newLow, newMed, newHigh};
        toneCount = new int[] {0,0,0};
        ran = new Random();
        gen = new SoundGenerator();
        steps = time / 2;
        lastTone = -1;
        status = 0;
    }

    public void run() {
        cont = true;
        for( int step = 0; step < steps && cont; step++ ) { // Note the two part conditional
            status = 0;
            int tone = ran.nextInt(3);
            lastTone = tone;
            totalTone += 1;
            incCount(tone);

            toneCount[tone] += 1;

            switch( tone ) {
                case 0:
                    gen.produceLowTone(1000);
                    break;

                case 1:
                    gen.produceMediumTone(1000);
                    break;

                case 2:
                    gen.produceHighTone(1000);
                    break;
            }
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            writeLog();
        }
        gen.shutdown();

        Logger.println( "Tone 1 count: " + toneCount[0]);
        Logger.println( "Tone 2 count: " + toneCount[1]);
        Logger.println( "Tone 3 count: " + toneCount[2]);

        Logger.println( "Correct: " + correct + "; False Positive: " + falsePos );
        Platform.exit();
    }

    public void buttonPressed( int toneLevel ) {
        totalPress += 1;
        if( getCount(toneLevel) == desired[toneLevel] ){
            status = 1;
            correct += 1;
        } else {
            status = -1;
            falsePos += 1;
        }
        resetCount(toneLevel);
    }

    public void resetCount( int index ){
        synchronized( lock ) {
            counts[index] = 0;
        }
    }

    public void incCount( int index ) {
        synchronized( lock ) {
            counts[index] += 1;
        }
    }

    public int getCount( int index ) {
        int value = -1;
        synchronized( lock ) {
            value = counts[index];
        }
        return value;
    }

    public void stop() {
        if( cont ) {
            cont = false;
        }
    }

    private void writeLog() {
        Logger.print(LocalDateTime.now().toLocalTime().toString() + ":   ");

        Logger.print("[" + getCount(0) + ", " + getCount(1) + ", " + getCount(2) + "],");
        Logger.print(lastTone + ", ");
        Logger.println(Integer.toString(status));
    }

}
