/**
 * Created by tjc1575 on 6/17/15.
 */
public class Demo {
    public static void main(String[] args) {
        SoundGenerator gen = new SoundGenerator();
        try {
            gen.produceLowTone(1000);
            Thread.sleep(1000);
            gen.produceMediumTone(1000);
            Thread.sleep(1000);
            gen.produceHighTone(1000);
            Thread.sleep(1000);
            gen.produceHighTone(1000);
            Thread.sleep(1000);
            gen.produceMediumTone(1000);
            Thread.sleep(1000);
            gen.produceLowTone(1000);
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
