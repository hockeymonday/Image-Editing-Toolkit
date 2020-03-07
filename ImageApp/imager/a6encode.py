"""
Steganography methods for the imager application.

This module provides all of the test processing operations (encode, decode)
that are called by the application. Note that this class is a subclass of Filter.
This allows us to layer this functionality on top of the Instagram-filters,
providing this functionality in one application.

Based on an original file by Dexter Kozen (dck10) and Walker White (wmw2)

Author: Adam Kadhim (ak779) and Calvin Johnson (clj78)
Date:   November 20, 2019
"""
import a6filter


class Encoder(a6filter.Filter):
    """
    A class that contains a collection of image processing methods

    This class is a subclass of Filter.  That means it inherits all of the
    methods and attributes of that class too. We do that separate the
    steganography methods from the image filter methods, making the code
    easier to read.

    Both the `encode` and `decode` methods should work with the most recent
    image in the edit history.
    """

    def encode(self, text):
        """
        Returns True if it could hide the text; False otherwise.

        This method attemps to hide the given message text in the current
        image. This method first converts the text to a byte list using the
        encode() method in string to use UTF-8 representation:

            blist = list(text.encode('utf-8'))

        This allows the encode method to support all text, including emojis.

        The method indicates the start of the message with the monoalphabetic
        values of 'hidden' encoded in the first 6 pixels with succesive values
        in front such that:

            The values 7,8,3,3,4,13 (monoalphabetic for 'Hidden') turn into...
                17,28,33,43,54,113

            *Note that 13 (monoalphabetic 'n') was arbitrarily turned into
             113 since 613 would have been too large (> 255)

        The same methodology is applied to indicate the end of the message with
        the monoalphabetic values of 'end' encoded in the last 3 pixels with
        succesive values in front in the same way as before.

        This method also makes sure there are enough pixels to encode to begin
        with since 9 are needed for the begining and end phrase on top of
        however many bytes the text is.

        If the text UTF-8 encoding requires more than 999999 bytes or the
        picture does not have enough pixels to store these bytes, this method
        returns False without storing the message. However, if the number of
        bytes is both less than 1000000 and less than (# pixels - 10), then
        the encoding should succeed.  So this method uses no more than 10
        pixels to store additional encoding information.

        Parameter text: a message to hide
        Precondition: text is a string
        """
        #assert preconditions
        assert type(text) == str, 'text must be a string'

        current = self.getCurrent()
        byte_list = list(text.encode('utf-8'))
        #encoding does not proceed if its more than a 999999 bytes
        if len(byte_list) > 999999:
            return False

        #Start and end values to encode
        starter_bytes = [17,28,33,43,54,113]
        end_bytes = [14,213,33]
        x=0
        y=6
        z=6

        #Makes sure image has enough pixels to encode full message
        pixels_needed = len(starter_bytes) + len(end_bytes) + len(byte_list)
        if len(current) <= pixels_needed:
            return False

        #This is a marker at begining indicating encoding from first 6 pixels
        for byte in starter_bytes:
            self._encode_pixel(x,byte)
            x+=1

        #This is a marker indicating the end of the message with end_byte values
        for bite in end_bytes:
            self._encode_pixel(len(byte_list)+y, bite)
            y+=1

        #This encodes the message
        for bhyte in byte_list:
            self._encode_pixel(z,bhyte)
            z+=1

        return True

    def decode(self):
        """
        Returns the secret message (a string) stored in the current image.

        The message should be decoded as a list of bytes. Assuming that a list
        blist has only bytes (ints in 0.255), you can turn it into a string
        using UTF-8 with the decode method:

            text = bytes(blist).decode('utf-8')

        If no message is detected, or if there is an error in decoding the
        message, this method returns None
        """
        current = self.getCurrent()
        start = []
        start_compare = [17,28,33,43,54,113]
        end_pos = 0
        text_bytes = []

        try:
            #Look for intro indicator
            for x in range(0,6):
                num1 = self._decode_pixel(x)
                start.append(num1)

            assert start == start_compare,'start indicator not found'

            #Look for end indicator, values are 14,213,33
            for x in range(len(current)):
                if (self._decode_pixel(x) == 14 and self._decode_pixel(x+1) == 213
                    and self._decode_pixel(x+2) == 33):
                    end_pos = x
                    break

            #Now we can decode the text
            for x in range(6,end_pos):
                num3 = self._decode_pixel(x)
                text_bytes.append(num3)

            message = bytes(text_bytes)
            return message.decode('utf-8')

        except:
            return None

    # HELPER METHODS
    def _decode_pixel(self, pos):
        """
        Return: the number n hidden in pixel pos of the current image.

        This function assumes that the value was a 3-digit number encoded as
        the last digit in each color channel (e.g. red, green and blue).

        Parameter pos: a pixel position
        Precondition: pos is an int with  0 <= p < image length (as a 1d list)
        """
        current = self.getCurrent()

        #Assert preconditions
        assert type(pos) == int, 'pos must be an integer'
        assert 0<= pos and pos<len(current),'range must be 0<= pos<image length'

        rgb = current[pos]
        red   = rgb[0]
        green = rgb[1]
        blue  = rgb[2]
        return  (red % 10) * 100  +  (green % 10) * 10  +  blue % 10

    def _encode_pixel(self, pos, byte):
        """
        Alters pixel at given position (row,col) to encode a 3 digit byte value
        into the rgb values of the pixel.

        This method takes the position of a pixel and encodes a given 3 digit
        byte value in the last number of the red, green, and blue values of the
        pixel of the given position.

        Parameter pos: a pixel position
        Precondition: pos is an int with  0 <= p < image length (as a 1d list)

        Paramter byte: a byte value to encode in a pixel
        Precondition: byte is an int with 0 <= byte <= 255
        """
        current = self.getCurrent()

        #assert preconditions
        assert type(pos) == int, 'pos must be an integer'
        assert 0<= pos and pos<len(current),'range must be 0<= pos <image length'
        assert type(byte) == int,'byte must be an int'
        assert 0<=byte and byte<=255,'byte must be between 0 and 255 (inclusive)'

        rgb = current[pos]
        new_rgb = list(rgb)
        byte = str(byte)
        if len(byte) == 2:
            byte = '0' + byte
        elif len(byte) == 1:
            byte = '00' + byte

        #Changes the last digit of each rgb value of given pixel
        for x in range(0,len(byte)):
            color = str(rgb[x])
            color = color[:-1]   #cut off last digit
            color = color+byte[x]
            color = int(color)
            if color > 255:
                color = color - 10
            new_rgb[x] = color

        #Sets the pixel to the encrypted rgb values
        new_rgb = tuple(new_rgb)
        current[pos] = new_rgb
