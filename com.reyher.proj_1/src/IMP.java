/*
 *Hunter Lloyd
 * Copyrite.......I wrote, ask permission if you want to use it outside of class. 
 */

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.File;
import java.awt.image.PixelGrabber;
import java.awt.image.MemoryImageSource;

import java.util.prefs.Preferences;



class IMP implements MouseListener{
   JFrame frame;
   JPanel mp;
   JButton start;
   JScrollPane scroll;
   JMenuItem openItem, exitItem, resetItem;
   Toolkit toolkit;
   File pic;
   ImageIcon img;
   int colorX, colorY;
   int [] pixels;
   int [] results;
   //Instance Fields you will be using below
   
   //This will be your height and width of your 2d array
   int height=0, width=0;
   int firstHeight;
   int firstWidth;
   
   //your 2D array of pixels
    int picture[][];

    /* 
     * In the Constructor I set up the GUI, the frame the menus. The open pulldown 
     * menu is how you will open an image to manipulate. 
     */
   IMP()
   {
      toolkit = Toolkit.getDefaultToolkit();
      frame = new JFrame("Image Processing Software by Hunter");
      JMenuBar bar = new JMenuBar();
      JMenu file = new JMenu("File");
      JMenu functions = getFunctions();
      frame.addWindowListener(new WindowAdapter(){
            @Override
              public void windowClosing(WindowEvent ev){quit();}
            });
      openItem = new JMenuItem("Open");
      openItem.addActionListener(new ActionListener(){
            @Override
          public void actionPerformed(ActionEvent evt){ handleOpen(); }
           });
      resetItem = new JMenuItem("Reset");
      resetItem.addActionListener(new ActionListener(){
            @Override
          public void actionPerformed(ActionEvent evt){ reset(); }
           });     
      exitItem = new JMenuItem("Exit");
      exitItem.addActionListener(new ActionListener(){
            @Override
          public void actionPerformed(ActionEvent evt){ quit(); }
           });
      file.add(openItem);
      file.add(resetItem);
      file.add(exitItem);
      bar.add(file);
      bar.add(functions);
      frame.setSize(600, 600);
      mp = new JPanel();
      mp.setBackground(new Color(0, 0, 0));
      scroll = new JScrollPane(mp);
      frame.getContentPane().add(scroll, BorderLayout.CENTER);
      JPanel butPanel = new JPanel();
      butPanel.setBackground(Color.black);
      start = new JButton("start");
      start.setEnabled(false);
      start.addActionListener(new ActionListener(){
            @Override
          public void actionPerformed(ActionEvent evt){ fun1(); }
           });
      butPanel.add(start);
      frame.getContentPane().add(butPanel, BorderLayout.SOUTH);
      frame.setJMenuBar(bar);
      frame.setVisible(true);      
   }
   
   /* 
    * This method creates the pulldown menu and sets up listeners to selection of the menu choices. If the listeners are activated they call the methods 
    * for handling the choice, fun1, fun2, fun3, fun4, etc. etc. 
    */
   
  private JMenu getFunctions()
  {
     JMenu fun = new JMenu("Functions");
     
     JMenuItem firstItem = new JMenuItem("MyExample - fun1 method");
     JMenuItem grayscale = new JMenuItem("Gray!");
     JMenuItem equalize = new JMenuItem("Equalizer!");
     JMenuItem histogram = new JMenuItem("Histogram!!");
     JMenuItem edge_map = new JMenuItem("Edge map (5x5)");
     JMenuItem rotate = new JMenuItem("Spin me!");
     JMenuItem blur = new JMenuItem("Blur!");
    
     firstItem.addActionListener(new ActionListener(){
            @Override
          public void actionPerformed(ActionEvent evt){fun1();}
           });

     rotate.addActionListener(new ActionListener() {
         @Override
         public void actionPerformed(ActionEvent e) {
             rotate_ninety();
         }
     });

     grayscale.addActionListener(new ActionListener() {
         @Override
         public void actionPerformed(ActionEvent evt) {
             turn_to_grayscale();
         }
     });

     blur.addActionListener(new ActionListener() {
         @Override
         public void actionPerformed(ActionEvent e) {
             blur();
         }
     });

     equalize.addActionListener(new ActionListener() {
         @Override
         public void actionPerformed(ActionEvent e) {
             equalize();
         }
     });

     histogram.addActionListener(new ActionListener() {
         @Override
         public void actionPerformed(ActionEvent e) {
             histogram();
         }
     });

     edge_map.addActionListener(new ActionListener() {
         @Override
         public void actionPerformed(ActionEvent e) {
             edge_map();
         }
     });
   
       
      fun.add(firstItem);
      fun.add(rotate);
      fun.add(grayscale);
      fun.add(blur);
      fun.add(equalize);
      fun.add(histogram);
      fun.add(edge_map);
     
      return fun;   

  }
  
  /*
   * This method handles opening an image file, breaking down the picture to a one-dimensional array and then drawing the image on the frame. 
   * You don't need to worry about this method. 
   */
    private void handleOpen()
  {  
     img = new ImageIcon();
     JFileChooser chooser = new JFileChooser();
      Preferences pref = Preferences.userNodeForPackage(IMP.class);
      String path = pref.get("DEFAULT_PATH", "");

      chooser.setCurrentDirectory(new File(path));
     int option = chooser.showOpenDialog(frame);
     
     if(option == JFileChooser.APPROVE_OPTION) {
        pic = chooser.getSelectedFile();
        pref.put("DEFAULT_PATH", pic.getAbsolutePath());
       img = new ImageIcon(pic.getPath());
      }
     width = img.getIconWidth();
     height = img.getIconHeight();
     firstWidth = width;
     firstHeight = height;
     
     JLabel label = new JLabel(img);
     label.addMouseListener(this);
     pixels = new int[width*height];
     
     results = new int[width*height];
  
          
     Image image = img.getImage();
        
     PixelGrabber pg = new PixelGrabber(image, 0, 0, width, height, pixels, 0, width );
     try{
         pg.grabPixels();
     }catch(InterruptedException e)
       {
          System.err.println("Interrupted waiting for pixels");
          return;
       }
     for(int i = 0; i<width*height; i++)
        results[i] = pixels[i];  
     turnTwoDimensional();
     mp.removeAll();
     mp.add(label);
     
     mp.revalidate();
  }
  
  /*
   * The libraries in Java give a one dimensional array of RGB values for an image, I thought a 2-Dimensional array would be more usefull to you
   * So this method changes the one dimensional array to a two-dimensional. 
   */
  private void turnTwoDimensional()
  {
     picture = new int[height][width];
     for(int i=0; i<height; i++)
       for(int j=0; j<width; j++)
          picture[i][j] = pixels[i*width+j];
      
     
  }
  /*
   *  This method takes the picture back to the original picture
   */
  private void reset()
  {
        for(int i = 0; i<width*height; i++)
             pixels[i] = results[i]; 
       Image img2 = toolkit.createImage(new MemoryImageSource(width, height, pixels, 0, width)); 

      JLabel label2 = new JLabel(new ImageIcon(img2));
      //label2.addMouseListener(this);
       mp.removeAll();
       mp.repaint();
       mp.add(label2);
     
       mp.revalidate();
       width = firstWidth;
       height = firstHeight;
       turnTwoDimensional();
    }
  /*
   * This method is called to redraw the screen with the new image. 
   */
  private void resetPicture()
  {
       for(int i=0; i<height; i++)
       for(int j=0; j<width; j++)
          pixels[i*width+j] = picture[i][j];
      Image img2 = toolkit.createImage(new MemoryImageSource(width, height, pixels, 0, width)); 

      JLabel label2 = new JLabel(new ImageIcon(img2));    
       mp.removeAll();
       mp.add(label2);
     
       mp.revalidate();
       mp.repaint();
   
    }
    /*
     * This method takes a single integer value and breaks it down doing bit manipulation to 4 individual int values for A, R, G, and B values
     */
  private int [] getPixelArray(int pixel)
  {
      int temp[] = new int[4];
      temp[0] = (pixel >> 24) & 0xff;
      temp[1]   = (pixel >> 16) & 0xff;
      temp[2] = (pixel >>  8) & 0xff;
      temp[3]  = (pixel      ) & 0xff;
      return temp;
      
    }
    /*
     * This method takes an array of size 4 and combines the first 8 bits of each to create one integer. 
     */
  private int getPixels(int rgb[])
  {
         int alpha = 0;
         int rgba = (rgb[0] << 24) | (rgb[1] <<16) | (rgb[2] << 8) | rgb[3];
        return rgba;
  }
  
  public void getValue()
  {
      int pix = picture[colorY][colorX];
      int temp[] = getPixelArray(pix);
      System.out.println("Color value " + temp[0] + " " + temp[1] + " "+ temp[2] + " " + temp[3]);
    }
  
  /**************************************************************************************************
   * This is where you will put your methods. Every method below is called when the corresponding pulldown menu is 
   * used. As long as you have a picture open first the when your fun1, fun2, fun....etc method is called you will 
   * have a 2D array called picture that is holding each pixel from your picture. 
   *************************************************************************************************/
   /*
    * Example function that just removes all red values from the picture. 
    * Each pixel value in picture[i][j] holds an integer value. You need to send that pixel to getPixelArray the method which will return a 4 element array 
    * that holds A,R,G,B values. Ignore [0], that's the Alpha channel which is transparency, we won't be using that, but you can on your own.
    * getPixelArray will breaks down your single int to 4 ints so you can manipulate the values for each level of R, G, B. 
    * After you make changes and do your calculations to your pixel values the getPixels method will put the 4 values in your ARGB array back into a single
    * integer value so you can give it back to the program and display the new picture. 
    */

    /**
     *
     * @param row
     * @param col
     * function takes both params and locates a given pixel
     * @return array containing 24 pixels surrounding pixel given in params
     */
  private int[][] five_by_five_values(int row, int col){
      int[][] rgb = new int[24][4];

      int i = -2;
      int[] temp = new int[4];
      temp[0] = 255;

      while(i < 3){
          if(row > 1 && col > 1 && row < height - 2 && col < width - 2) {
              //top row
              rgb[(i + 2)] = getPixelArray(picture[row - 2][col + i]);
              //2nd row
              rgb[i + 7] = getPixelArray(picture[row - 1][col + i]);
          }else{
              rgb[(i + 2)] = temp;
              rgb[i + 7] = temp;
              }
          if(row > 1 && col > 1 && row < height - 2 && col < width - 2) {
              //4th row
              rgb[i + 12] = getPixelArray(picture[row + 1][col + i]);
              //last row
              rgb[i + 17] = getPixelArray(picture[row + 2][col + i]);
          }else{
              rgb[i + 12] = temp;
              rgb[i + 17] = temp;
          }
          i++;
      }
      if(row > 1 && col > 1 && row < height - 2 && col < width - 2) {
          rgb[20] = getPixelArray(picture[row][col - 2]);
          rgb[21] = getPixelArray(picture[row][col - 1]);
          rgb[22] = getPixelArray(picture[row][col + 1]);
          rgb[23] = getPixelArray(picture[row][col + 2]);
      }else{
          rgb[20] = temp;
          rgb[21] = temp;
          rgb[22] = temp;
          rgb[23] = temp;
      }

      return(rgb);
  }

  // returns average color between 3 channels in given pixel
  private int pixel_avg(int[] pixel){
      return((pixel[1] + pixel[2] + pixel[3]) / 3);
    }
  private void fun1()
  {
     
    for(int i=0; i<height; i++)
       for(int j=0; j<width; j++)
       {   
          int rgbArray[] = new int[4];
         
          //get three ints for R, G and B
          rgbArray = getPixelArray(picture[i][j]);
         
        
           rgbArray[1] = 0;
           //take three ints for R, G, B and put them back into a single int
           picture[i][j] = getPixels(rgbArray);
        } 
     resetPicture();
  }

  private void rotate_ninety() {
      // create array with height and width switched from original picture (for odd images)
      int[][] temp = new int[width][height];

      // switch (transpose) rows and columns into temp
      for(int i = 0; i < height; i++){
          for(int j = 0; j < width; j++){
              temp[j][i] = picture[i][j];
          }
      }

      // reverse each column - thanks (https://stackoverflow.com/questions/21920939/reverse-the-rows-of-a-2d-array)
      for(int j = 0; j < temp.length; j++){
          for(int i = 0; i < temp[j].length / 2; i++) {
              int temp_row = temp[j][i];
              temp[j][i] = temp[j][temp[j].length - i - 1];
              temp[j][temp[j].length - i - 1] = temp_row;
          }
      }

      picture = temp;
      int temp_w = width;
      // reset width and height to avoid index explosions
      width = height;
      height = temp_w;
      resetPicture();

  }
  private void turn_to_grayscale() {
      for (int row = 0; row < height; row++) {
          for (int col = 0; col < width; col++) {
              int[] rgbArray;

              rgbArray = getPixelArray(picture[row][col]);
              // math for grayscale
              int luminous = (int) ((rgbArray[1] * 0.21) + (rgbArray[2] * 0.72) +  (rgbArray[3] * 0.07));
              // change all values (gray)
              rgbArray[1] = luminous;
              rgbArray[2] = luminous;
              rgbArray[3] = luminous;

              picture[row][col] = getPixels(rgbArray);
          }
      }
      resetPicture();
  }

  private void blur() {
      int[][] temp = picture;
      for(int row = 0; row < height; row++) {
          for (int col = 0; col < width; col++) {
              // get 5x5 map of pixels around current pixel
              int[][] pixels = five_by_five_values(row, col);
              int red_avg = 0, green_avg = 0, blue_avg = 0;
              // take average of each pixel
              for(int[] pixel : pixels){
                  red_avg += pixel[1];
                  green_avg += pixel[2];
                  blue_avg += pixel[3];
              }
              //24 or 25 should work fine
              red_avg /= 24;
              green_avg /= 24;
              blue_avg /= 24;
              // replace current pixel with average of surrounding
              int[] final_array = new int[4];
              final_array[0] = 255;
              final_array[1] = red_avg;
              final_array[2] = green_avg;
              final_array[3] = blue_avg;

              temp[row][col] = getPixels(final_array);

          }
      }
      picture = temp;
      resetPicture();

  }

  private void edge_map() {
        int[][] temp = picture;

        for(int row = 0; row < height; row++){
            for(int col = 0; col < width; col++){
                //get 5x5 values for surrounding pixles
                int[][] mask = five_by_five_values(row, col);
                // take an average of the surrounding pixels (outermost are multiplied by -1, center is x16)
                int running_avg = 0;
                //top row and 2nd row
                for(int i = 0; i < 6; i++) {
                    running_avg += (-1 * pixel_avg(mask[i]));
                }
                running_avg += (-1 * pixel_avg(mask[9]));
                //middle row
                running_avg += (-1 * pixel_avg(mask[20]));
                //current pixel
                running_avg += (16 * pixel_avg(getPixelArray(picture[row][col])));
                running_avg += (-1 * pixel_avg(mask[23]));
                //4th row
                running_avg += (-1 * pixel_avg(mask[10]));
                running_avg += (-1 * pixel_avg(mask[14]));
                //last row
                for(int i = 15; i < 20; i++){
                    running_avg += (-1 * pixel_avg(mask[i]));
                }

                running_avg /= 25;

                int[] new_pixel = new int[4];
                new_pixel[0] = 255;
                // arbitrary constant threshold - above = white pixel - below = black pixel
                if(running_avg > 45){
                    new_pixel[1] = 255;
                    new_pixel[2] = 255;
                    new_pixel[3] = 255;
                }else{
                    new_pixel[1] = 0;
                    new_pixel[2] = 0;
                    new_pixel[3] = 0;
                }
                temp[row][col] = getPixels(new_pixel);

            }
        }

        picture = temp;
        resetPicture();
  }

    /**
     * Given a color (i.e. "red"), return a histogram array, of frequencies of pixel intensities.
     * @param color
     * @return array
     */
  private int[] get_histogram(String color){

      int[] arr = new int[256];
      for(int row = 0; row < height; row ++){
          for(int col = 0; col < width; col++){
              int[] pixel = getPixelArray(picture[row][col]);
              switch (color) {
                  case "red":
                      arr[pixel[1]]++;
                  case "green":
                      arr[pixel[2]]++;
                  case "blue":
                      arr[pixel[3]]++;
              }
          }
      }
      return arr;
  }
  private void histogram() {
      int[] red_array = new int[256];
      int[] green_array = new int[256];
      int[] blue_array = new int[256];


      //gather histograms of color channels
      red_array = get_histogram("red");
      green_array = get_histogram("green");
      blue_array = get_histogram("blue");

      //def frame
      JFrame histo_frame = new JFrame();
      histo_frame.setLayout(new BorderLayout(0,0));
      histo_frame.setSize(900, 350);

      //three panels will sit in one frame, each have their own corresponding background color
      MyPanel red_panel = new MyPanel(red_array);
      MyPanel green_panel = new MyPanel(green_array);
      MyPanel blue_panel = new MyPanel(blue_array);

      //red
      red_panel.setBackground(Color.red);
      red_panel.setLayout(new FlowLayout(FlowLayout.LEFT));
      red_panel.setOpaque(true);
      red_panel.setPreferredSize(new Dimension(300,300));
      histo_frame.add(red_panel, BorderLayout.WEST);

      //green
      green_panel.setBackground(Color.green);
      green_panel.setLayout(new FlowLayout(FlowLayout.CENTER));
      green_panel.setPreferredSize(new Dimension(300,300));
      histo_frame.add(green_panel, BorderLayout.CENTER);

      //blue
      blue_panel.setLayout(new FlowLayout(FlowLayout.RIGHT));
      blue_panel.setBackground(Color.blue);
      blue_panel.setPreferredSize(new Dimension(300,300));
      histo_frame.add(blue_panel, BorderLayout.EAST);


      histo_frame.setVisible(true);

  }

  //note - will not work on RAW images due to the nature of maximum number values wrapping around (use small image for good results)
  private void equalize() {
      int[][] temp = picture;

      //each color channel will go through the same steps for this whole function
      int[] red_array = new int[256];
      int[] green_array = new int[256];
      int[] blue_array = new int[256];

      //grab histograms of intensity frequencies
      red_array = get_histogram("red");
      green_array = get_histogram("green");
      blue_array = get_histogram("blue");

      int total_pixels = width * height;
      double[] red_cdf = new double[256];
      double[] green_cdf = new double[256];
      double[] blue_cdf = new double[256];


      int red_sum=0, blue_sum=0, green_sum=0;
      //create cumulative distribution function
      for(int i = 0; i < 256; i ++){
          red_sum += red_array[i];
          red_cdf[i] =  red_sum * 255 / (double) total_pixels;

          green_sum += green_array[i];
          green_cdf[i] = green_sum * 255 / (double) total_pixels;

          blue_sum += blue_array[i];
          blue_cdf[i] = blue_sum * 255 / (double) total_pixels;
      }
      // find max and min of each cdf array
      double red_max = 0, red_min = width * height;
      double blue_max = 0, blue_min = width * height;
      double green_max = 0, green_min = width * height;

      for(int i = 0; i < 256; i++){
            if(red_cdf[i] > red_max){
                red_max = red_cdf[i];
            }
            if(red_cdf[i] < red_min){
                red_min = red_cdf[i];
            }
          if(green_cdf[i] > green_max){
              green_max = green_cdf[i];
          }
          if(green_cdf[i] < green_min){
              green_min = green_cdf[i];
          }
          if(blue_cdf[i] > blue_max){
              blue_max = blue_cdf[i];
          }
          if(blue_cdf[i] < blue_min){
              blue_min = blue_cdf[i];
          }
      }

      // normalize every value in cdf array
      // val - max / max - min
      for(int i = 0; i < 256; i++){
          red_cdf[i] = (red_cdf[i] - red_max) / (red_max - red_min);
          green_cdf[i] = (green_cdf[i] - green_max) / (green_max - green_min);
          blue_cdf[i] = (blue_cdf[i] - blue_max) / (blue_max - blue_min);
      }
      double[] red_norm = new double[256];
      double[] green_norm = new double[256];
      double[] blue_norm = new double[256];

      //reverse signs in the array (normalization was a bit funky)
      for(int i = 0; i < 256; i++){
          red_norm[i] =  Math.abs(red_cdf[i]) * 255.0;
          green_norm[i] = Math.abs(green_cdf[i]) * 255;
          blue_norm[i] = Math.abs(blue_cdf[i]) * 255;
      }
      //reverse arrays or there will be anti-equalization
      int[] rev_array = new int[256];
      int j = 255;
      for(int i = 0; i < rev_array.length; i++){
          rev_array[i] = j;
          j --;
      }

      //map each pixel to a new value via its reversed intensity
      for(int row = 0; row < height; row ++){
          for(int col = 0; col < width; col++) {
                int[] temp_pixel = new int[4];
                int[] pixel = getPixelArray(picture[row][col]);

                temp_pixel[0] = 255;
                temp_pixel[1] = (int) red_norm[rev_array[pixel[1]]];
                temp_pixel[2] = (int) green_norm[rev_array[pixel[2]]];
                temp_pixel[3] = (int) blue_norm[rev_array[pixel[3]]];


                temp[row][col] = getPixels(temp_pixel);
          }
      }

      picture = temp;
      resetPicture();
  }
  
  private void quit()
  {  
     System.exit(0);
  }

    @Override
   public void mouseEntered(MouseEvent m){}
    @Override
   public void mouseExited(MouseEvent m){}
    @Override
   public void mouseClicked(MouseEvent m){
        colorX = m.getX();
        colorY = m.getY();
        System.out.println(colorX + "  " + colorY);
        getValue();
        start.setEnabled(true);
    }
    @Override
   public void mousePressed(MouseEvent m){}
    @Override
   public void mouseReleased(MouseEvent m){}
   
   public static void main(String [] args)
   {

       IMP imp = new IMP();
   }
 
}