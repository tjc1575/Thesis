import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.effect.Glow;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyCodeCombination;
import javafx.scene.layout.Background;

import java.awt.*;

public class Controller {
    @FXML
    Button low_button;

    @FXML
    Button medium_button;

    @FXML
    Button high_button;

    Glow glow = new Glow(0.75);


    public void setAccelerators() {

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
       if( event.getSource() == low_button ) {
           //highlightButton(low_button);
           System.out.println( "Low" );
       } else if ( event.getSource() == medium_button ) {
           System.out.println( "Medium" );
       } else if ( event.getSource() == high_button ) {
           System.out.println( "High" );
       } else {
           System.err.println("Invalid button press");
       }
   }

    protected void highlightButton( final Button button ) {
        button.setEffect(glow);
        new Thread( ()->{
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            button.setEffect(null);}
        ).start();
    }


}
