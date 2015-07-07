/*
    Filename: Main.java
    Author: Taylor Carpenter <tjc1575@rit.edu>

    Main class for RanTask application. Performs setup based on configuration
    files before starting the JavaFX application. It presents tones to the
    user in a random order, logging when a tone is presented and when
    the user presses a key.
 */

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
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Scanner;


public class Main extends Application {

    Parent root; // Root of the JavaFX application as defined by the fxml
    Controller controller; // Controller that handles user interaction
    SoundGenerator gen; // Generates the tones presented to the user
    TaskController task; // Controls the task logic as defined by the config
    Map<String,String> config; // Configuration values

    /*
        Initialize the JavaFX application by reading in the fxml. Also creates
        the controller for event handling and the sound generator.
     */
    //@Override
    public void init() throws Exception {
        super.init();
        FXMLLoader loader = new FXMLLoader(getClass().getResource("rantask.fxml"));
        root = loader.load();
        controller = loader.getController();
        gen = new SoundGenerator();
        config = new HashMap<String,String>();
    }

    /*
        Presents an input dialog so that the participant id can
        be read in for logging purposes.
        This dialog is meant for the study coordinator.
     */
    private void presentInputDialog_Participant() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("Participant Number Input Dialog");
        dialog.setHeaderText("");
        dialog.setContentText("Please enter the participant id:");

        Optional<String> result = dialog.showAndWait();

        // Initializes participant value to 000 in case something goes wrong with the
        // dialog results.
        config.put("participant", "000");
        result.ifPresent(subID -> config.put("participant", subID));
    }

    /*
        Presents an input dialog so that the config file location can be specified.
        This dialog is meant for the study coordinator.
     */
    private void presentInputDialog_Config() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("Config File Input Dialog");
        dialog.setHeaderText("");
        dialog.setContentText("Please enter the config file location:");

        Optional<String> result = dialog.showAndWait();

        result.ifPresent(filename -> processConfig(filename));
    }

    /*
        Presents a dialog to the participant. When dismissed, the main program
        will begin.
     */
    private void presentBeginDialog() {
        Alert alert = new Alert( Alert.AlertType.INFORMATION );
        alert.setHeaderText("");
        alert.setContentText("Click 'OK' to begin.");
        alert.setTitle("RanTask Start");
        alert.showAndWait();
    }

    /*
        Starts the JavaFX application. Multiple dialog boxes, directed at both the
        study coordinator and the participant are presented before the main
        task begins.
     */
    public void start(Stage primaryStage) throws Exception{
        presentInputDialog_Participant();
        presentInputDialog_Config();

        // Create task controller based on the config values.
        task = new TaskController(Integer.parseInt(config.get("low"))
                , Integer.parseInt(config.get("medium"))
                , Integer.parseInt(config.get("high"))
                , Integer.parseInt(config.get("duration")));


        primaryStage.setTitle("RanTask");
        primaryStage.setScene(new Scene(root, 600, 200));
        controller.setup( task ); // Connect the controller to the task controller for event handling.
        primaryStage.show();

        presentBeginDialog();

        // Log the expected values specified by the config and the start time to simplify
        // processing of study results.
        Logger.println( "Expected: " + config.get("low") + ", " + config.get("medium") + ", " + config.get("high"));
        Logger.println(LocalDateTime.now().toLocalTime().toString());

        // Start auditory task on its own thread.
        new Thread( task ).start();
    }

    /*
        On stop of the JavaFX application, stop the auditory task as well, if necessary, and
        present the participant with an information window so the exit is not abrupt.
     */
    @Override
    public void stop() {
        task.stop();

        Alert alert = new Alert( Alert.AlertType.INFORMATION );
        alert.setHeaderText("");
        alert.setContentText("Click 'OK' to exit.");
        alert.setTitle("RanTask End");
        alert.showAndWait();

        Logger.close();
    }

    /*
        Process the given configuration file for log file location,
        duration, and tone count targets. File reading errors are
        not handled gracefully and issues with configuration will
        cause crashes down the line.
     */
    private void processConfig( String filename ) {
        Scanner scan = null;
        try {
            scan = new Scanner( new File(filename) );
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        // Configuration file is in the format of one configuration per line,
        // each configuration being 'key: value'.
        while( scan.hasNextLine() ) {
            String line = scan.nextLine();
            String[] comp = line.split(": ");
            config.put( comp[0], comp[1] );
        }

        // Create the path to the log file. Log file consists of participant id and start time.
        Path path = Paths.get(config.get("log_location"));
        path = path.resolve( (config.get("participant") + "_" + LocalDateTime.now()+".dat").replace(':', '_'));

        try {
            Logger.setFile(path.toString()); // Set the output file of the logger.
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

    }

    /*
        Prints usage message to standard error.
     */
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
