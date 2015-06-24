import javafx.animation.FillTransition;
import javafx.animation.PauseTransition;
import javafx.animation.SequentialTransition;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyCodeCombination;

import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.util.Duration;

import java.time.LocalDateTime;


public class Controller {
    @FXML
    Button low_button;

    @FXML
    Circle low_toggle;

    SequentialTransition low_st;

    @FXML
    Button medium_button;

    @FXML
    Circle medium_toggle;

    SequentialTransition medium_st;

    @FXML
    Button high_button;

    @FXML
    Circle high_toggle;

    SequentialTransition high_st;

    final Duration SEC_HALF = Duration.millis(500);
    final Duration SEC_QUART = Duration.millis(250);

    TaskController task;

    public void setup( TaskController task ) {
        setAccelerators();
        low_st = createAnimation( low_toggle );
        medium_st = createAnimation( medium_toggle );
        high_st = createAnimation( high_toggle );
        this.task = task;
    }

    protected SequentialTransition createAnimation( Circle circle ) {
        Color filledColor = Color.DODGERBLUE;
        Color emptyColor = Color.WHITE;
        FillTransition ft = new FillTransition( SEC_QUART, circle, emptyColor, filledColor );
        PauseTransition pt = new PauseTransition(SEC_HALF);
        FillTransition et = new FillTransition( SEC_QUART, circle, filledColor, emptyColor );
        return new SequentialTransition( ft, pt, et );
    }

    protected void setAccelerators() {

        setButtonAccelerator(low_button, KeyCode.DIGIT1);
        setButtonAccelerator(medium_button, KeyCode.DIGIT2);
        setButtonAccelerator(high_button, KeyCode.DIGIT3);

    }

    protected void setButtonAccelerator( final Button button, KeyCode key ) {
        Scene scene = button.getScene();
        if( scene == null ) {
            throw new IllegalArgumentException("setButtonAccelerator must be called on an active button.");
        }

        scene.getAccelerators().put(
                new KeyCodeCombination( key ),
                () -> { button.fire(); }
        );
    }

   @FXML
    protected void handleButtonAction(ActionEvent event) {
       Logger.print(LocalDateTime.now().toLocalTime().toString() + ":   ");
       if (event.getSource() == low_button) {
           task.buttonPressed(0);
           low_st.playFromStart();
           Logger.println("Low");
       } else if (event.getSource() == medium_button) {
           task.buttonPressed(1);
           medium_st.playFromStart();
           Logger.println("Medium");
       } else if (event.getSource() == high_button) {
           task.buttonPressed(2);
           high_st.playFromStart();
           Logger.println("High");
       } else {
           System.err.println("Invalid button press");
       }
   }
}
