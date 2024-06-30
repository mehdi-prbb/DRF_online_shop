from django.contrib.auth.models import UserManager



class CustomUserManager(UserManager):
	"""
	Custom manager for CustomUser model.
    Provides helper methods for creating regular users and superusers.
	"""
	def create_user(self, email, password):
		"""
		Creates and returns a regular user with the given email and password.
		"""
		if not email:
			raise ValueError('user must have phone number')

		email = self.normalize_email(email)
		user = self.model(
				email=email
				)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password):
		"""
		Creates and returns a superuser with the given email and password.
		"""
		user = self.create_user(email, password)
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)