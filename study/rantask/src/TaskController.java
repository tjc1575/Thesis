/*
    Filename: TaskController.java
    Author: Taylor Carpenter <tjc1575@rit.edu>

    Controller for the auditory task. Runs a separate thread that
    presents the tones in a random order and handles button presses from
    the user.
 */

import javafx.application.Platform;
import java.time.LocalDateTime;
import java.util.Random;


public class TaskController implements Runnable{
    private static final Object lock = new Object();
    private Random ran; // Random number generator
    private SoundGenerator gen;
    private int steps = 0; // Total number of tones to be played this trial

    private int[] counts; // Number of times each tone response was pressed
    private int[] desired; // The count cycle desired for each tone
    private int[] toneCount; // The number of times each tone was presented

    private int correct = 0; // The number of times the participant responded correctly
    private int falsePos = 0; // The number of times the participant responded incorrectly

    private int lastTone; // The last tone that was presented ( 1 for low, 2 for medium, 3 for high )
    private int status; // -1 if the last tone was responded to incorrectly, 0 if no responds, 1 if correct

    private boolean cont; // Flag used to stop the run cycle if the program is exited


    public TaskController( int low, int medium, int high, int time ) {
        // Set desired counts to -1 if they are to be ignored to aid logic
        int newLow = low == 0 ? -1 : low;
        int newMed = medium == 0 ? -1 : medium;
        int newHigh = high == 0 ? -1 : high;

        counts = new int[] {0,0,0};
        desired = new int[] {newLow, newMed, newHigh};
        toneCount = new int[] {0,0,0};
        ran = new Random();
        gen = new SoundGenerator();
        steps = time / 2; // Each tone is 1 second plus 1 second of pause so the number of tones is half the time
        lastTone = -1;
        status = 0;
    }

    public void run() {
        cont = true;
        for( int step = 0; step < steps && cont; step++ ) { // Note the two part conditional
            status = 0;
            int tone = ran.nextInt(3); // Generate random tone
            lastTone = tone;
            incCount(tone);

            toneCount[tone] += 1;

            switch (tone) {
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

        gen.shutdown(); // Shutdown sound generator

        // Log final tone counts
        Logger.println( "Tone 1 count: " + toneCount[0]);
        Logger.println( "Tone 2 count: " + toneCount[1]);
        Logger.println( "Tone 3 count: " + toneCount[2]);

        // Log performance
        Logger.println( "Correct: " + correct + "; False Positive: " + falsePos );
        Platform.exit();
    }

    /*
        Called when a button corresponding to the given tone is pressed. Increases the
        response count for the tone, resets the count cycle, and updates correct / false positive.
     */
    public void buttonPressed( int toneLevel ) {
        if( getCount(toneLevel) == desired[toneLevel] ){
            status = 1;
            correct += 1;
        } else {
            status = -1;
            falsePos += 1;
        }
        resetCount(toneLevel);
    }

    /*
        Resets the count cycle for the given index. Thread safe.
     */
    public void resetCount( int index ){
        synchronized( lock ) {
            counts[index] = 0;
        }
    }

    /*
        Increments the count cycle for the given index. Thread safe.
     */
    public void incCount( int index ) {
        synchronized( lock ) {
            counts[index] += 1;
        }
    }

    /*
        Returns the current value in the count cycle for the
        given index. Thread safe.
     */
    public int getCount( int index ) {
        int value = -1;
        synchronized( lock ) {
            value = counts[index];
        }
        return value;
    }

    /*
        Set the cont flag to stop the run loop.
     */
    public void stop() {
        if( cont ) {
            cont = false;
        }
    }

    /*
        Write a log message out to the Logger specifying the time, most recent tone,
        current tone counts, and the user status.
     */
    private void writeLog() {
        Logger.print(LocalDateTime.now().toLocalTime().toString() + ":   ");

        Logger.print("[" + getCount(0) + ", " + getCount(1) + ", " + getCount(2) + "],");
        Logger.print(lastTone + ", ");
        Logger.println(Integer.toString(status));
    }

}
