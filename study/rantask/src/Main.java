import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.stage.Stage;


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

        processConfig();
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
        task.stop();

        Alert alert = new Alert( Alert.AlertType.INFORMATION );
        alert.setHeaderText("");
        alert.setContentText("Click 'OK' to exit.");
        alert.setTitle("RanTask End");
        alert.showAndWait();
    }

    private void processConfig() {

    }

    public static void usage() {
        System.err.println( "Usage: java rantask subject_id config_file");
    }

    public static void main(String[] args) {
        if( args.length != 2 ) {
            usage();
            return;
        }

        Logger.setup();
        launch(args);



    }
}
