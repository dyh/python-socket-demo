# python socket demo

transfer binary image files and text message via python socket. 


# Requirements

- python 3.6+, pip 20+
- pip install -r requirements.txt

    ```
    numpy
    Pillow
    opencv-python
    ```

# How to run

1. prepare some image files:
    ```
    copy image files to "./images/" folder, make file path as: 
    "./images/0001.png", "./images/0002.png", "./images/0003.png", etc.
    ```
   
2. run test-server:

    ```
    python test-server.py
    ```

3. run test-client:

    ```
    python test-client.py
    ```
