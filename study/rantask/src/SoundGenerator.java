import javax.sound.midi.MidiChannel;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.MidiUnavailableException;
import javax.sound.midi.Synthesizer;

/**
 * Created by tjc1575 on 6/6/15.
 */
public class SoundGenerator {

    private Synthesizer synth;
    private MidiChannel channel;

    public SoundGenerator() {
        try {
            synth = MidiSystem.getSynthesizer();
            synth.open();
            MidiChannel chan[] = synth.getChannels();
            for( MidiChannel mChan : chan ) {
                if( mChan != null ) {
                    channel = mChan;
                    break;
                }
            }
            channel.setSolo(true);
        } catch (MidiUnavailableException e) {
            e.printStackTrace();
        }
    }

    public void produceLowTone( long time ) {
        produceTone( 71, time );
    }

    public void produceMediumTone( long time ) {
        produceTone( 77, time );
    }

    public void produceHighTone( long time ) {
        produceTone( 80, time );
    }

    private void produceTone( int note, long time ) {
        channel.noteOn(note,100);
        try {
            Thread.sleep(time);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        channel.allNotesOff();
    }

    public void shutdown() {
        synth.close();
    }
}
