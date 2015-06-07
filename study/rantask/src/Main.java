import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

import javax.sound.midi.MidiChannel;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.MidiUnavailableException;
import javax.sound.midi.Synthesizer;

public class Main extends Application {

    Parent root;
    Controller controller;
    SoundGenerator gen;

    //@Override
    public void init() throws Exception {
        super.init();
        FXMLLoader loader = new FXMLLoader(getClass().getResource("rantask.fxml"));
        root = loader.load();
        controller = loader.getController();
        gen = new SoundGenerator();
    }

    public void start(Stage primaryStage) throws Exception{

        gen.produceLowTone(1000);

        primaryStage.setTitle("Hello World");
        primaryStage.setScene(new Scene(root, 600, 200));
        controller.setAccelerators();
        primaryStage.show();
    }


    public static void main(String[] args) {

        //launch(args);
        TaskController cont = new TaskController(0,3,0,30);
        new Thread( cont ).start();
    }
}
