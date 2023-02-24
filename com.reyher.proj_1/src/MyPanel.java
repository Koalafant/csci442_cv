
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;

public class MyPanel extends JPanel
{
 
int startX, flag, startY, endX, endY;

    BufferedImage grid;
    Graphics2D gc;
    int[] colors;

	public MyPanel(int[] color_array)
	{
        colors = color_array;
	   startX = startY = 0;
       endX = endY = 255;
       grid = new BufferedImage(300,300, BufferedImage.TYPE_INT_ARGB);
       gc = grid.createGraphics();
       drawing();
 	}

     public void clear()
    {
       grid = null;
       repaint();
    }
    public void paintComponent(Graphics g)
    {  
         super.paintComponent(g);
         Graphics2D g2 = (Graphics2D)g;
         if(grid == null){
            int w = this.getWidth();
            int h = this.getHeight();
            grid = (BufferedImage)(this.createImage(w,h));
            gc = grid.createGraphics();

         }
         g2.drawImage(grid, null, 0, 0);
     }
    public void drawing()
    {
        gc.setColor(Color.black);
        int min = 99999999;
        int max = 0;

        //find max and min values of color histograms
        for(int i = 0; i < colors.length; i++){
            if(colors[i] < min){
                min = colors[i];
            }
            if(colors[i] > max){
                max = colors[i];
            }
        }
        //avoid divide by 0
        if(min == 0){
            min = 1;
        }
        //draw a normalized histogram (slightly more readable)
        for(int i = 0; i < colors.length - 1; i++){
            float val = (float) (((float) colors[i] - min) / ((float) max - min));
            gc.drawLine(i, 500, i, 300 - (int) (val * 255));
        }
        repaint();
    }
   
}
