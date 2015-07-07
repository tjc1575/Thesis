/*
    Filename: Demo.java
    Author: Taylor Carpenter <tjc1575@rit.edu>

    Demo for the auditory task to allow participants to become
    familiar with the individual tones. Presents the tones in the
    following order: low, medium, high, high, medium, low.
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
