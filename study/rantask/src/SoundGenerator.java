/*
    Filename: SoundGenerator.java
    Author: Taylor Carpenter <tjc1575@rit.edu>

    Generates sounds of the desired frequency synthesized using the
    midi sound system.
 */
import javax.sound.midi.MidiChannel;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.MidiUnavailableException;
import javax.sound.midi.Synthesizer;

public class SoundGenerator {

    private Synthesizer synth; // Synthesizer to generate sounds.
    private MidiChannel channel; // Midi channel on which to play sounds.

    public SoundGenerator() {
        try {
            synth = MidiSystem.getSynthesizer();
            synth.open();

            // Grab a midi channel, is doesn't matter which one.
            MidiChannel chan[] = synth.getChannels();
            for( MidiChannel mChan : chan ) {
                if( mChan != null ) {
                    channel = mChan;
                    break;
                }
            }

            channel.setSolo(true); // Mute all other channels.
        } catch (MidiUnavailableException e) {
            e.printStackTrace();
        }
    }

    /*
        Produce a B4 note for the desired time.
     */
    public void produceLowTone( long time ) {
        produceTone( 71, time );
    }

    /*
        Produce an F5 note for the desired time.
     */
    public void produceMediumTone( long time ) {
        produceTone( 77, time );
    }

    /*
        Produce a A5 note for the desired time.
     */
    public void produceHighTone( long time ) {
        produceTone( 80, time );
    }

    /*
        Produce the desired midi note for the desired amount of time.
        There is a maximum time the note can be played because the intensity drops
        off and eventually will be inaudible.
     */
    private void produceTone( int note, long time ) {
        channel.noteOn(note,100);
        try {
            Thread.sleep(time);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        channel.allNotesOff();
    }

    /*
        Close the synthesizer to free up resources.
     */
    public void shutdown() {
        synth.close();
    }
}
