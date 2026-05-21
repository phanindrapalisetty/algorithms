# track dod revenue

# orders: 
# users: 
# payments: 
# products: 

# Grain at which analyst queries: product_id, order_id, date

# fct_orders: 
# 	- date
# 	- order_id 
# 	- user_id 
# 	- order_status 
# 	- address_city
# 	- payemnt_status
# 	- payment_id 
# 	- product_id
# 	- product_category
# 	- product_cart_price


# dim_date: date, FY, Querters - 

# dim_order: 
# 	- order_flow_id - surrogate key for this dimension
# 	- order_id
# 	- order_status
# 	- order_details: city, address, pincode, 
# 	- user_id 
# 	- is_active

# dim_user: 
# 	- user_sk
# 	- user_id
# 	- user_details: email, personal_details, phone number etc.
# 	- is_active: 
# 	- address: {
# 		1: {
# 			true/false
# 		}
# 	} -- How? 

# dim_user_details: 
# 	- SCD Type 2

# dim_payments: 
# 	- payment_id 
# 	- payment_status
# 	- payment_details


# cart -> payment -> order placed -> Shipping -> Delivered -> Return window closed -> Returned 


# status in ('Delivered', 'Return window closed', 'Returned')



# order: Delivered 


# and order_date >= '1st May'  and status in ('Delivered', 'Return window closed', 'Returned'); 




# 1st May orders as of 21st: 

# Total Order Value: 1Cr (14-day window)

# 10L: Delivered
# 70L: return Closed
# 20L: Returned 


# 20th May order as of 21st: 

# 90L: Delivered
# 1L: return Closed
# 9L: Returned 




