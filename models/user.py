class HealthyMeUser:

    def __init__(
        self,
        username,
        nickname,
        birthday,
        height,
        weight
    ):
        self.username = username
        self.nickname = nickname
        self.birthday = birthday
        self.height = height
        self.weight = weight

    def calculate_bmi(self):

        height_m = self.height / 100

        if height_m <= 0:
            return 0

        return self.weight / (height_m ** 2)