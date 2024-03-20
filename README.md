# Scissor API Documentation

Welcome to Scissor API, In today’s world, it’s important to keep things as short as possible, and this applies to more concepts than you may realize. From music, and speeches, to wedding receptions, brief is the new black. Scissor is a simple tool that makes URLs as short as possible.

### Base URL

The base URL for accessing Scissor API is:

`https://scissor-url.onrender.com`



#### States

##### Get All States

Endpoint: `/states`

Method: GET

Description: Retrieves all states in Nigeria.

Response Body: Array of state objects.

##### Get State by ID

Endpoint: `/states/{state_id}`

Method: GET

Description: Retrieves state details by ID.

Response Body: State object.

##### Get State by Name

Endpoint: `/states/state/{stateSearch}`

Method: GET

Description: Retrieves state details by name.

Response Body: State object.

#### LGAs

##### Get All LGAs

Endpoint: `/lgas`

Method: GET

Description: Retrieves all local government areas (LGAs) in Nigeria.

Response Body: Array of LGA objects.

##### Get LGA by ID

Endpoint: `/lgas/{lga_id}`

Method: GET

Description: Retrieves LGA details by ID.

Response Body: LGA object.

#### Cities

##### Get All Cities

Endpoint: `/cities`

Method: GET

Description: Retrieves all cities in Nigeria.

Response Body: Array of city objects.

##### Get City by ID

Endpoint: `/cities/{city_id}`

Method: GET

Description: Retrieves city details by ID.

Response Body: City object.

### Conclusion

Locale API provides comprehensive access to geographical information about Nigeria, empowering developers to build innovative solutions tailored to the needs of Nigeria's diverse population. By leveraging Locale's endpoints and authentication mechanisms, developers can seamlessly integrate geographical data into their applications, unlocking new possibilities for exploration and development. Start exploring Nigeria with Locale API today!