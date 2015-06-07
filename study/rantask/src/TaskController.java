import java.util.Random;

/**
 * Created by tjc1575 on 6/6/15.
 */
public class TaskController implements Runnable{
    private static final Object lock = new Object();
    private Random ran;
    private SoundGenerator gen;
    private int steps = 0;

    int[] counts;
    int[] desired;

    int totalTone = 0;
    int totalPress = 0;
    int correct = 0;
    int falsePos = 0;

    public TaskController( int low, int medium, int high, int time ) {
        counts = new int[] {0,0,0};
        desired = new int[] {low, medium, high};
        ran = new Random();
        gen = new SoundGenerator();
        steps = time / 2;
    }

    public void run() {
        for( int step = 0; step < steps; step++ ) {
            int tone = ran.nextInt(3);
            totalTone += 1;
            incCount(tone);
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
        }
        gen.shutdown();
    }

    public void buttonPressed( int toneLevel ) {
        totalPress += 1;
        if( getCount(toneLevel) == desired[toneLevel] ){
            correct += 1;
        } else {
            falsePos += 1;
        }

        resetCount(toneLevel );
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

}
