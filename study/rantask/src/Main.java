import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.stage.Stage;


import javax.sound.midi.MidiChannel;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.MidiUnavailableException;
import javax.sound.midi.Synthesizer;

public class Main extends Application {

    Parent root;
    Controller controller;
    SoundGenerator gen;
    TaskController task;

    //@Override
    public void init() throws Exception {
        super.init();
        FXMLLoader loader = new FXMLLoader(getClass().getResource("rantask.fxml"));
        root = loader.load();
        controller = loader.getController();
        gen = new SoundGenerator();
        task = new TaskController(1,3,-1,30);
    }

    public void start(Stage primaryStage) throws Exception{

        primaryStage.setTitle("RanTask");
        primaryStage.setScene(new Scene(root, 600, 200));
        controller.setup( task );
        primaryStage.show();

        Alert alert = new Alert( Alert.AlertType.INFORMATION );
        alert.setHeaderText("");
        alert.setContentText("Click 'OK' to begin.");
        alert.setTitle("RanTask Start");
        alert.showAndWait();

        new Thread( task ).start();
    }

    @Override
    public void stop() {
        Alert alert = new Alert( Alert.AlertType.INFORMATION );
        alert.setHeaderText("");
        alert.setContentText("Click 'OK' to exit.");
        alert.setTitle("RanTask End");
        alert.showAndWait();
    }


    public static void main(String[] args) {

        launch(args);



    }
}
