# Function to calculate azimuth and elevation
def calculate_az_el(df):
    E = np.array(df['SunPosE'])
    N = -np.array(df['SunPosN'])
    U = np.array(df['SunPosU'])
    Az_deg = np.degrees(np.arctan2(E, N))
    El_deg = np.degrees(np.arctan2(U, np.sqrt(E**2 + N**2)))
    return Az_deg, El_deg

def num_to_name(helID):
    """Returns the name of a heliostat based on its ID"""
    str_ = str(helID)
    name = chr(ord('A') + int(str_[0]) - 1)
    name += chr(ord('A') + int(str_[1:3]) - 1)
    name += str_[3:]
    return name