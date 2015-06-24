import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.TextInputDialog;
import javafx.stage.Stage;

import java.io.File;
import java.io.FileNotFoundException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.*;
import java.util.regex.Pattern;


public class Main extends Application {

    Parent root;
    Controller controller;
    SoundGenerator gen;
    TaskController task;
    Map<String,String> config;

    //@Override
    public void init() throws Exception {
        super.init();
        FXMLLoader loader = new FXMLLoader(getClass().getResource("rantask.fxml"));
        root = loader.load();
        controller = loader.getController();
        gen = new SoundGenerator();
        config = new HashMap<String,String>();
    }

    private void presentInputDialog_Participant() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("Participant Number Input Dialog");
        dialog.setHeaderText("");
        dialog.setContentText("Please enter the participant id:");

        Optional<String> result = dialog.showAndWait();

        config.put("participant", "000");
        result.ifPresent(subID -> config.put("participant", subID));
    }

    private void presentInputDialog_Config() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("Config File Input Dialog");
        dialog.setHeaderText("");
        dialog.setContentText("Please enter the config file location:");

        Optional<String> result = dialog.showAndWait();

        result.ifPresent(filename -> processConfig(filename));
    }

    private void presentBeginDialog() {
        Alert alert = new Alert( Alert.AlertType.INFORMATION );
        alert.setHeaderText("");
        alert.setContentText("Click 'OK' to begin.");
        alert.setTitle("RanTask Start");
        alert.showAndWait();

        Logger.println(LocalDateTime.now().toLocalTime().toString());
    }

    public void start(Stage primaryStage) throws Exception{
        presentInputDialog_Participant();
        presentInputDialog_Config();

        task = new TaskController(Integer.parseInt(config.get("low"))
                , Integer.parseInt(config.get("medium"))
                , Integer.parseInt(config.get("high"))
                , Integer.parseInt(config.get("duration")));


        primaryStage.setTitle("RanTask");
        primaryStage.setScene(new Scene(root, 600, 200));
        controller.setup( task );
        primaryStage.show();

        presentBeginDialog();

        new Thread( task ).start();
    }

    @Override
    public void stop() {
        task.stop();

        Alert alert = new Alert( Alert.AlertType.INFORMATION );
        alert.setHeaderText("");
        alert.setContentText("Click 'OK' to exit.");
        alert.setTitle("RanTask End");
        alert.showAndWait();
    }

    private void processConfig( String filename ) {
        Scanner scan = null;
        try {
            scan = new Scanner( new File(filename) );
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        while( scan.hasNextLine() ) {
            String line = scan.nextLine();
            String[] comp = line.split(": ");
            config.put( comp[0], comp[1] );
        }

        Path path = Paths.get(config.get("log_location"));
        path = path.resolve( (config.get("participant") + "_" + LocalDateTime.now()+".dat").replace(':', '_'));

        try {
            Logger.setFile(path.toString());
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

    }

    public static void usage() {
        System.err.println( "Usage: java rantask");
    }

    public static void main(String[] args) {
        if( args.length != 0 ) {
            usage();
            return;
        }

        Logger.setup();
        launch(args);



    }
}
